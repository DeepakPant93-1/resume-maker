package com.learning.resumemaker.model;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** Payload returned to the UI for one resume. */
@Builder
@Schema(description = "A stored resume")
public record ResumeResponse(
		String id,
		Metadata metadata,
		Profile profile,
		List<Experience> experience,
		List<Education> education,
		Skills skills,
		List<Project> projects,
		List<Certification> certifications,
		List<SpokenLanguage> spokenLanguages) {
}
