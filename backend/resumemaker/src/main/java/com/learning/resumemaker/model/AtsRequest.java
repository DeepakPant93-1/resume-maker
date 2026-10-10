package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/**
 * A resume to score for ATS, plus an optional job description (with it the score includes keyword match).
 * It is the body of both the UI's call and the call on to the agent service.
 */
@Builder
@Schema(description = "A resume to score, optionally against a job description")
public record AtsRequest(
		@NotNull(message = "A resume is required") @Valid ResumeRequest resume,
		@Size(max = 20000) String jobDescription) {
}
