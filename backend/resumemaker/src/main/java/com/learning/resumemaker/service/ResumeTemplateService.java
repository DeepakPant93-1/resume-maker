package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.StringWriter;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.TemplateNotFoundException;
import com.learning.resumemaker.model.ResumeTemplate;

import freemarker.cache.ClassTemplateLoader;
import freemarker.core.TemplateClassResolver;
import freemarker.template.Configuration;
import freemarker.template.DefaultObjectWrapperBuilder;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;
import lombok.extern.slf4j.Slf4j;

/**
 * The LaTeX resume templates in {@code src/main/resources/templates/} and the rendering of a resume into one.
 * <p>
 * Templates are Apache FreeMarker files with the square-bracket syntax (see the header of {@code classic.tex}) and
 * {@link ResumeDocument} as the data model. A {@code .tex} file is offered only if it has placeholders and parses:
 * a file without placeholders (a filled sample) would print the same resume for everyone.
 */
@Slf4j
@Service
public class ResumeTemplateService {

	private static final String TEMPLATE_DIR = "templates";
	private static final String EXTENSION = ".tex";
	private static final String PLACEHOLDER = "[=";
	private static final Pattern COMMENT_LINE = Pattern.compile("(?m)^[ \\t]*%.*(?:\\r?\\n|$)");

	private final Configuration freemarker;
	private final List<ResumeTemplate> templates;

	/** Sets up FreeMarker and finds the usable templates once, at startup. */
	public ResumeTemplateService() {
		this.freemarker = createConfiguration();
		this.templates = findTemplates();
		log.info("Loaded {} resume template(s): {}", templates.size(),
				templates.stream().map(ResumeTemplate::id).collect(Collectors.joining(", ")));
	}

	/** The templates a resume can be downloaded in, by name. */
	public List<ResumeTemplate> listTemplates() {
		return templates;
	}

	/**
	 * Fills a template with a resume.
	 *
	 * @param templateId id from {@link #listTemplates()}, e.g. "classic"
	 * @param resume     the resume to fill in
	 * @return the LaTeX source
	 * @throws TemplateNotFoundException if there is no such template
	 */
	public String renderTemplate(String templateId, ResumeDocument resume) {
		ResumeTemplate template = templates.stream().filter(t -> t.id().equals(templateId)).findFirst()
				.orElseThrow(() -> new TemplateNotFoundException(templateId));
		StringWriter out = new StringWriter();
		try {
			freemarker.getTemplate(template.id() + EXTENSION).process(resume, out);
		} catch (IOException ex) {
			throw new UncheckedIOException("Could not read template " + template.id(), ex);
		} catch (TemplateException ex) {
			throw new IllegalStateException("Could not render template " + template.id(), ex);
		}
		return withoutCommentLines(out.toString());
	}

	/**
	 * Drops lines that hold only a LaTeX comment (the template's documentation and its "% [#if]" directive lines)
	 * and squeezes the blank lines left behind, so users get clean source. TeX ignores such lines entirely, so the
	 * PDF does not change; a comment after code on the same line is kept.
	 */
	private static String withoutCommentLines(String latex) {
		return COMMENT_LINE.matcher(latex).replaceAll("").replaceAll("\\n{3,}", "\n\n").strip() + "\n";
	}

	/** FreeMarker set up the way the templates expect: square-bracket syntax, UTF-8, errors thrown to the caller. */
	private static Configuration createConfiguration() {
		Configuration cfg = new Configuration(Configuration.VERSION_2_3_34);
		cfg.setTemplateLoader(new ClassTemplateLoader(ResumeTemplateService.class, "/" + TEMPLATE_DIR));
		cfg.setTagSyntax(Configuration.SQUARE_BRACKET_TAG_SYNTAX);
		cfg.setInterpolationSyntax(Configuration.SQUARE_BRACKET_INTERPOLATION_SYNTAX);
		cfg.setDefaultEncoding(StandardCharsets.UTF_8.name());
		cfg.setLocalizedLookup(false);
		cfg.setObjectWrapper(new DefaultObjectWrapperBuilder(Configuration.VERSION_2_3_34).build());
		cfg.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
		cfg.setLogTemplateExceptions(false);
		cfg.setWrapUncheckedExceptions(true);
		cfg.setNewBuiltinClassResolver(TemplateClassResolver.ALLOWS_NOTHING_RESOLVER);
		return cfg;
	}

	/** Every {@code .tex} file in the templates folder that has placeholders and parses, sorted by name. */
	private List<ResumeTemplate> findTemplates() {
		Resource[] files;
		try {
			files = new PathMatchingResourcePatternResolver()
					.getResources("classpath*:" + TEMPLATE_DIR + "/*" + EXTENSION);
		} catch (IOException ex) {
			throw new UncheckedIOException("Could not list the resume templates", ex);
		}
		return Arrays.stream(files).filter(this::isUsableTemplate)
				.map(file -> idOf(file.getFilename()))
				.distinct()
				.map(id -> new ResumeTemplate(id, displayName(id)))
				.sorted(Comparator.comparing(ResumeTemplate::name))
				.toList();
	}

	/** True if the file has placeholders and FreeMarker can parse it; a broken one is skipped with a warning. */
	private boolean isUsableTemplate(Resource file) {
		String name = file.getFilename();
		try {
			if (!file.getContentAsString(StandardCharsets.UTF_8).contains(PLACEHOLDER)) {
				log.debug("Skipping {}: no placeholders", name);
				return false;
			}
			freemarker.getTemplate(name);
			return true;
		} catch (IOException ex) {
			log.warn("Skipping template {}: {}", name, ex.getMessage());
			return false;
		}
	}

	/** "classic.tex" -> "classic". */
	private static String idOf(String fileName) {
		return fileName.substring(0, fileName.length() - EXTENSION.length());
	}

	/** "modern-two_column" -> "Modern Two Column". */
	private static String displayName(String id) {
		return Arrays.stream(id.split("[-_ ]+")).filter(word -> !word.isEmpty())
				.map(word -> word.substring(0, 1).toUpperCase(Locale.ROOT) + word.substring(1))
				.collect(Collectors.joining(" "));
	}
}
