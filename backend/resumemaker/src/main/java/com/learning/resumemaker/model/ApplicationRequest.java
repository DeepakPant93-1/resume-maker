package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Payload the UI sends to track or update a job application. The id is never part of it. */
@Builder
@Schema(description = "A job application to track")
public record ApplicationRequest(
		@NotBlank @Size(max = 200) String company,
		@NotBlank @Size(max = 200) String role,
		@Schema(description = "The saved resume used for this application, if any") @Size(max = 64) String resumeId,
		@Schema(description = "Defaults to APPLIED") ApplicationStage stage) {
}
