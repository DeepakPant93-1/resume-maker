package com.learning.resumemaker.model;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Payload returned to the UI. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeResponse {

	private String id;
	private Metadata metadata;
	private Profile profile;
	private List<Experience> experience;
	private List<Education> education;
	private Skills skills;
	private List<Project> projects;
	private List<Certification> certifications;
	private List<SpokenLanguage> spokenLanguages;
}
