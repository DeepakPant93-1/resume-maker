package com.learning.resumemaker.document;

import java.time.Instant;
import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Database representation of a resume (MongoDB collection "resumes"). */
@Document(collection = "resumes")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeDocument {

	@Id
	private String id;
	/** The user who owns this resume (the subject of their login token). */
	@Indexed
	private String userId;
	private Metadata metadata;
	private Profile profile;
	private List<Experience> experience;
	private List<Education> education;
	private Skills skills;
	private List<Project> projects;
	private List<Certification> certifications;
	private List<SpokenLanguage> spokenLanguages;
	private Instant createdAt;
	private Instant updatedAt;

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Metadata {
		private String title;
		private String template;
		private Integer atsScore;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Profile {
		private String fullName;
		private String jobTitle;
		private String email;
		private String phone;
		private String location;
		private String linkedin;
		private String summary;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Experience {
		private String jobTitle;
		private String company;
		private String startDate;
		private String endDate;
		private boolean current;
		private String achievements;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Education {
		private String degree;
		private String university;
		private String startYear;
		private String endYear;
		private String grade;
		private String location;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Skills {
		private List<String> languages;
		private List<String> frameworks;
		private List<String> tools;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Project {
		private String name;
		private String description;
		private String technologies;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class Certification {
		private String name;
		private String issuer;
	}

	@Data
	@Builder
	@NoArgsConstructor
	@AllArgsConstructor
public static class SpokenLanguage {
		private String language;
		private String proficiency;
	}
}
