package com.learning.resumemaker.model;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Payload the UI sends to create or update a resume. The id is never part of it. */
@Builder
@Schema(description = "A resume to create, update, score or summarize")
public record ResumeRequest(
		@Valid Metadata metadata,
		@Valid Profile profile,
		@Size(max = 50) List<@Valid Experience> experience,
		@Size(max = 50) List<@Valid Education> education,
		@Valid Skills skills,
		@Size(max = 50) List<@Valid Project> projects,
		@Size(max = 50) List<@Valid Certification> certifications,
		@Size(max = 50) List<@Valid SpokenLanguage> spokenLanguages) {
}
