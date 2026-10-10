package com.learning.resumemaker.mapper;

import java.util.List;
import java.util.function.Function;

import org.springframework.stereotype.Component;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.model.Certification;
import com.learning.resumemaker.model.Education;
import com.learning.resumemaker.model.Experience;
import com.learning.resumemaker.model.Metadata;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.Project;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.Skills;
import com.learning.resumemaker.model.SpokenLanguage;

/** Converts between UI models and database documents. */
@Component
public class ResumeMapper {

	/** Builds the document to store from the UI payload; the owner and timestamps are set by the service. */
	public ResumeDocument toDocument(String id, ResumeRequest r) {
		return ResumeDocument.builder()
				.id(id)
				.metadata(metadata(r.metadata()))
				.profile(profile(r.profile()))
				.experience(list(r.experience(), this::experience))
				.education(list(r.education(), this::education))
				.skills(skills(r.skills()))
				.projects(list(r.projects(), this::project))
				.certifications(list(r.certifications(), this::certification))
				.spokenLanguages(list(r.spokenLanguages(), this::spokenLanguage))
				.build();
	}

	/** Builds the UI payload from a stored resume. */
	public ResumeResponse toResponse(ResumeDocument r) {
		return ResumeResponse.builder()
				.id(r.getId())
				.metadata(metadata(r.getMetadata()))
				.profile(profile(r.getProfile()))
				.experience(list(r.getExperience(), this::experience))
				.education(list(r.getEducation(), this::education))
				.skills(skills(r.getSkills()))
				.projects(list(r.getProjects(), this::project))
				.certifications(list(r.getCertifications(), this::certification))
				.spokenLanguages(list(r.getSpokenLanguages(), this::spokenLanguage))
				.build();
	}

	/** Maps one metadata entry to the stored form. */
	private ResumeDocument.Metadata metadata(Metadata s) {
		return s == null ? null : ResumeDocument.Metadata.builder()
				.title(s.title())
				.template(s.template())
				.atsScore(s.atsScore())
				.build();
	}

	/** Maps one profile entry to the stored form. */
	private ResumeDocument.Profile profile(Profile s) {
		return s == null ? null : ResumeDocument.Profile.builder()
				.fullName(s.fullName())
				.jobTitle(s.jobTitle())
				.email(s.email())
				.phone(s.phone())
				.location(s.location())
				.linkedin(s.linkedin())
				.summary(s.summary())
				.build();
	}

	/** Maps one experience entry to the stored form. */
	private ResumeDocument.Experience experience(Experience s) {
		return s == null ? null : ResumeDocument.Experience.builder()
				.jobTitle(s.jobTitle())
				.company(s.company())
				.startDate(s.startDate())
				.endDate(s.endDate())
				.current(s.current())
				.achievements(s.achievements())
				.build();
	}

	/** Maps one education entry to the stored form. */
	private ResumeDocument.Education education(Education s) {
		return s == null ? null : ResumeDocument.Education.builder()
				.degree(s.degree())
				.university(s.university())
				.startYear(s.startYear())
				.endYear(s.endYear())
				.grade(s.grade())
				.location(s.location())
				.build();
	}

	/** Maps one skills entry to the stored form. */
	private ResumeDocument.Skills skills(Skills s) {
		return s == null ? null : ResumeDocument.Skills.builder()
				.languages(s.languages())
				.frameworks(s.frameworks())
				.tools(s.tools())
				.build();
	}

	/** Maps one project entry to the stored form. */
	private ResumeDocument.Project project(Project s) {
		return s == null ? null : ResumeDocument.Project.builder()
				.name(s.name())
				.description(s.description())
				.technologies(s.technologies())
				.build();
	}

	/** Maps one certification entry to the stored form. */
	private ResumeDocument.Certification certification(Certification s) {
		return s == null ? null : ResumeDocument.Certification.builder()
				.name(s.name())
				.issuer(s.issuer())
				.build();
	}

	/** Maps one spoken language entry to the stored form. */
	private ResumeDocument.SpokenLanguage spokenLanguage(SpokenLanguage s) {
		return s == null ? null : ResumeDocument.SpokenLanguage.builder()
				.language(s.language())
				.proficiency(s.proficiency())
				.build();
	}

	/** Maps one metadata entry to the UI form. */
	private Metadata metadata(ResumeDocument.Metadata s) {
		return s == null ? null : Metadata.builder()
				.title(s.getTitle())
				.template(s.getTemplate())
				.atsScore(s.getAtsScore())
				.build();
	}

	/** Maps one profile entry to the UI form. */
	private Profile profile(ResumeDocument.Profile s) {
		return s == null ? null : Profile.builder()
				.fullName(s.getFullName())
				.jobTitle(s.getJobTitle())
				.email(s.getEmail())
				.phone(s.getPhone())
				.location(s.getLocation())
				.linkedin(s.getLinkedin())
				.summary(s.getSummary())
				.build();
	}

	/** Maps one experience entry to the UI form. */
	private Experience experience(ResumeDocument.Experience s) {
		return s == null ? null : Experience.builder()
				.jobTitle(s.getJobTitle())
				.company(s.getCompany())
				.startDate(s.getStartDate())
				.endDate(s.getEndDate())
				.current(s.isCurrent())
				.achievements(s.getAchievements())
				.build();
	}

	/** Maps one education entry to the UI form. */
	private Education education(ResumeDocument.Education s) {
		return s == null ? null : Education.builder()
				.degree(s.getDegree())
				.university(s.getUniversity())
				.startYear(s.getStartYear())
				.endYear(s.getEndYear())
				.grade(s.getGrade())
				.location(s.getLocation())
				.build();
	}

	/** Maps one skills entry to the UI form. */
	private Skills skills(ResumeDocument.Skills s) {
		return s == null ? null : Skills.builder()
				.languages(s.getLanguages())
				.frameworks(s.getFrameworks())
				.tools(s.getTools())
				.build();
	}

	/** Maps one project entry to the UI form. */
	private Project project(ResumeDocument.Project s) {
		return s == null ? null : Project.builder()
				.name(s.getName())
				.description(s.getDescription())
				.technologies(s.getTechnologies())
				.build();
	}

	/** Maps one certification entry to the UI form. */
	private Certification certification(ResumeDocument.Certification s) {
		return s == null ? null : Certification.builder()
				.name(s.getName())
				.issuer(s.getIssuer())
				.build();
	}

	/** Maps one spoken language entry to the UI form. */
	private SpokenLanguage spokenLanguage(ResumeDocument.SpokenLanguage s) {
		return s == null ? null : SpokenLanguage.builder()
				.language(s.getLanguage())
				.proficiency(s.getProficiency())
				.build();
	}

	/** Maps every element of a list, keeping null as null. */
	private static <S, T> List<T> list(List<S> source, Function<S, T> fn) {
		return source == null ? null : source.stream().map(fn).toList();
	}
}
