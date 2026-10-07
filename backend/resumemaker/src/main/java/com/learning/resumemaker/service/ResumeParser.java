package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;

import com.learning.resumemaker.exception.InvalidResumeFileException;
import com.learning.resumemaker.model.Certification;
import com.learning.resumemaker.model.Education;
import com.learning.resumemaker.model.Experience;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.Project;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.Skills;

import lombok.extern.slf4j.Slf4j;

/**
 * Rule-based resume parser: PDF to text (PDFBox), then heading/regex heuristics. No LLM involved, so no token cost,
 * but it only handles reasonably conventional layouts; anything it misses can be fixed in the editor.
 */
@Slf4j
@Component
public class ResumeParser {

	private static final Pattern EMAIL = Pattern.compile("[\\w.+-]+@[\\w-]+(\\.[\\w-]+)+");
	private static final Pattern PHONE = Pattern.compile("(\\+?\\d[\\d\\s().-]{8,}\\d)");
	private static final Pattern LINKEDIN = Pattern.compile("(?:https?://)?(?:www\\.)?linkedin\\.com/in/[\\w-]+/?",
			Pattern.CASE_INSENSITIVE);
	private static final String MONTH = "(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\\.?";
	private static final String DATE = "(?:" + MONTH + "\\s+)?(?:19|20)\\d{2}";
	private static final Pattern DATE_RANGE = Pattern.compile(
			"(" + DATE + ")\\s*(?:-|–|—|to)\\s*(" + DATE + "|present|current|now)", Pattern.CASE_INSENSITIVE);
	private static final Pattern BULLET = Pattern.compile("^\\s*[•●▪◦*\\-–·]\\s*");

	private static final Map<String, List<String>> HEADINGS = new LinkedHashMap<>();
	static {
		HEADINGS.put("summary", List.of("summary", "professional summary", "profile", "objective", "about me", "about"));
		HEADINGS.put("experience", List.of("experience", "work experience", "professional experience",
				"employment", "employment history", "work history"));
		HEADINGS.put("education", List.of("education", "academic background", "qualifications"));
		HEADINGS.put("skills", List.of("skills", "technical skills", "key skills", "core skills", "technologies"));
		HEADINGS.put("projects", List.of("projects", "personal projects", "key projects"));
		HEADINGS.put("certifications", List.of("certifications", "certificates", "licenses", "courses"));
	}

	public ResumeRequest parse(InputStream pdf) {
		try (PDDocument document = Loader.loadPDF(pdf.readAllBytes())) {
			String text = new PDFTextStripper().getText(document);
			log.info("Extracted {} characters from {} PDF page(s)", text.length(), document.getNumberOfPages());
			if (text.isBlank()) {
				log.warn("PDF has no extractable text (scanned/image-only?)");
			}
			return parseText(text);
		} catch (IOException e) {
			log.error("PDFBox failed to read the file", e);
			throw new InvalidResumeFileException("Could not read the PDF file", e);
		}
	}

	ResumeRequest parseText(String text) {
		List<String> lines = text.lines().map(String::strip).filter(l -> !l.isEmpty()).toList();
		Map<String, List<String>> sections = splitSections(lines);
		List<String> header = sections.getOrDefault("header", List.of());

		Profile profile = parseProfile(header, text);
		profile.setSummary(String.join(" ", sections.getOrDefault("summary", List.of())));
		log.debug("Detected sections: {}", sections.keySet());

		ResumeRequest parsed = ResumeRequest.builder()
				.profile(profile)
				.experience(parseExperience(sections.getOrDefault("experience", List.of())))
				.education(parseEducation(sections.getOrDefault("education", List.of())))
				.skills(parseSkills(sections.getOrDefault("skills", List.of())))
				.projects(parseProjects(sections.getOrDefault("projects", List.of())))
				.certifications(parseCertifications(sections.getOrDefault("certifications", List.of())))
				.build();
		log.info("Parsed resume: {} experience, {} education, {} projects, {} certifications",
				parsed.getExperience().size(), parsed.getEducation().size(), parsed.getProjects().size(),
				parsed.getCertifications().size());
		return parsed;
	}

	private Map<String, List<String>> splitSections(List<String> lines) {
		Map<String, List<String>> sections = new LinkedHashMap<>();
		String current = "header";
		for (String line : lines) {
			String heading = headingOf(line);
			if (heading != null) {
				current = heading;
				sections.putIfAbsent(current, new ArrayList<>());
			} else {
				sections.computeIfAbsent(current, k -> new ArrayList<>()).add(line);
			}
		}
		return sections;
	}

	private String headingOf(String line) {
		String normalized = line.replaceAll("[:\\s]+$", "").toLowerCase(Locale.ROOT);
		if (normalized.length() > 30) {
			return null;
		}
		return HEADINGS.entrySet().stream()
				.filter(e -> e.getValue().contains(normalized))
				.map(Map.Entry::getKey)
				.findFirst().orElse(null);
	}

	private Profile parseProfile(List<String> header, String fullText) {
		Profile profile = new Profile();
		profile.setFullName(header.isEmpty() ? null : header.get(0));
		profile.setEmail(find(EMAIL, fullText));
		profile.setLinkedin(find(LINKEDIN, fullText));
		profile.setPhone(find(PHONE, String.join("\n", header)));
		// First non-name header line without contact details is most likely the job title.
		header.stream().skip(1)
				.filter(l -> !EMAIL.matcher(l).find() && !PHONE.matcher(l).find() && !LINKEDIN.matcher(l).find())
				.findFirst().ifPresent(profile::setJobTitle);
		return profile;
	}

	private List<Experience> parseExperience(List<String> lines) {
		List<Experience> jobs = new ArrayList<>();
		Experience job = null;
		StringBuilder achievements = new StringBuilder();
		String pendingTitle = null;
		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i);
			Matcher range = DATE_RANGE.matcher(line);
			boolean nextIsDateLine = i + 1 < lines.size() && DATE_RANGE.matcher(lines.get(i + 1)).find();
			if (!range.find() && nextIsDateLine && !BULLET.matcher(line).find()) {
				pendingTitle = line; // "Title" on its own line, "Company  dates" on the next
				continue;
			}
			range.reset();
			if (range.find()) {
				if (job != null) {
					job.setAchievements(achievements.toString().strip());
					jobs.add(job);
				}
				achievements.setLength(0);
				job = new Experience();
				job.setStartDate(range.group(1));
				job.setEndDate(range.group(2));
				job.setCurrent(range.group(2).matches("(?i)present|current|now"));
				String rest = (line.substring(0, range.start()) + line.substring(range.end()))
						.replaceAll("^[\\s|,@\\-–—]+|[\\s|,@\\-–—]+$", "");
				if (pendingTitle != null) {
					job.setJobTitle(pendingTitle);
					job.setCompany(rest.isEmpty() ? null : rest);
				} else if (!rest.isEmpty()) {
					String[] parts = rest.split("\\s+(?:at|@|\\||-|–|—)\\s+|,\\s*", 2);
					job.setJobTitle(parts[0].strip());
					if (parts.length > 1) {
						job.setCompany(parts[1].strip());
					}
				}
				pendingTitle = null;
			} else if (job != null) {
				if (BULLET.matcher(line).find()) {
					achievements.append("• ").append(BULLET.matcher(line).replaceFirst("")).append('\n');
				} else if (job.getCompany() == null) {
					job.setCompany(line);
				} else if (achievements.length() > 0) {
					achievements.append(line).append('\n');
				}
			}
		}
		if (job != null) {
			job.setAchievements(achievements.toString().strip());
			jobs.add(job);
		}
		return jobs;
	}

	private List<Education> parseEducation(List<String> lines) {
		List<Education> items = new ArrayList<>();
		Education edu = null;
		for (String line : lines) {
			Matcher range = DATE_RANGE.matcher(line);
			boolean isDegree = line.matches("(?i).*\\b(b\\.?tech|m\\.?tech|b\\.?e|b\\.?sc|m\\.?sc|bachelor|master|ph\\.?d|diploma|mba|bca|mca)\\b.*");
			if (isDegree || edu == null) {
				edu = new Education();
				items.add(edu);
				edu.setDegree(range.find() ? line.substring(0, range.start()).strip() : line);
			}
			range = DATE_RANGE.matcher(line);
			if (range.find()) {
				edu.setStartYear(range.group(1));
				edu.setEndYear(range.group(2));
			} else if (edu.getUniversity() == null && !line.equals(edu.getDegree())) {
				edu.setUniversity(line);
			} else if (line.toLowerCase(Locale.ROOT).matches(".*\\b(cgpa|gpa|grade|%)\\b.*")) {
				edu.setGrade(line);
			}
		}
		return items;
	}

	private Skills parseSkills(List<String> lines) {
		List<String> languages = new ArrayList<>();
		List<String> frameworks = new ArrayList<>();
		List<String> tools = new ArrayList<>();
		for (String line : lines) {
			String label = "";
			String values = BULLET.matcher(line).replaceFirst("");
			int colon = values.indexOf(':');
			if (colon > 0) {
				label = values.substring(0, colon).toLowerCase(Locale.ROOT);
				values = values.substring(colon + 1);
			}
			List<String> target = label.contains("language") ? languages
					: label.contains("framework") || label.contains("platform") || label.contains("librar") ? frameworks
					: tools;
			for (String skill : values.split("[,|•;]")) {
				if (!skill.isBlank()) {
					target.add(skill.strip());
				}
			}
		}
		return Skills.builder().languages(languages).frameworks(frameworks).tools(tools).build();
	}

	private List<Project> parseProjects(List<String> lines) {
		List<Project> projects = new ArrayList<>();
		Project project = null;
		StringBuilder description = new StringBuilder();
		for (String line : lines) {
			String lower = line.toLowerCase(Locale.ROOT);
			boolean bullet = BULLET.matcher(line).find();
			if (project != null && (lower.startsWith("technologies") || lower.startsWith("tech stack"))) {
				project.setTechnologies(line.substring(line.indexOf(':') + 1).strip());
			} else if (!bullet && (project == null || description.length() > 0)) {
				if (project != null) {
					project.setDescription(description.toString().strip());
					projects.add(project);
					description.setLength(0);
				}
				project = Project.builder().name(line).build();
			} else if (project != null) {
				description.append(BULLET.matcher(line).replaceFirst("")).append(' ');
			}
		}
		if (project != null) {
			project.setDescription(description.toString().strip());
			projects.add(project);
		}
		return projects;
	}

	private List<Certification> parseCertifications(List<String> lines) {
		return lines.stream()
				.map(l -> BULLET.matcher(l).replaceFirst(""))
				.map(l -> {
					// The issuer follows the last separator ("Name - Level - Issuer").
					Matcher sep = Pattern.compile("\\s+(?:-|–|—|\\|)\\s+").matcher(l);
					int start = -1;
					int end = -1;
					while (sep.find()) {
						start = sep.start();
						end = sep.end();
					}
					return start < 0 ? Certification.builder().name(l.strip()).build()
							: Certification.builder().name(l.substring(0, start).strip())
									.issuer(l.substring(end).strip()).build();
				})
				.toList();
	}

	private static String find(Pattern pattern, String text) {
		Matcher m = pattern.matcher(text);
		return m.find() ? m.group().strip() : null;
	}
}
