package com.learning.resumemaker.model;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Payload the UI sends to create/update a resume. The id is never part of it. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeRequest {

	private Metadata metadata;
	private Profile profile;
	private List<Experience> experience;
	private List<Education> education;
	private Skills skills;
	private List<Project> projects;
	private List<Certification> certifications;
	private List<SpokenLanguage> spokenLanguages;
}
