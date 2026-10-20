package com.learning.resumemaker.model;

import java.time.Instant;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** One tracked job application, as returned to the UI. */
@Builder
@Schema(description = "A tracked job application")
public record ApplicationResponse(
		String id,
		String company,
		String role,
		String resumeId,
		ApplicationStage stage,
		Instant createdAt,
		Instant updatedAt) {
}
