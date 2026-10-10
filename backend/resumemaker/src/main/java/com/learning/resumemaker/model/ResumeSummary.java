package com.learning.resumemaker.model;

import java.time.Instant;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** One row of the user's resume list (the dashboard): enough to show a card, not the whole resume. */
@Builder
@Schema(description = "One card of the resume list")
public record ResumeSummary(
		String id,
		String title,
		@Schema(description = "ATS score from the last save, or null if it could not be computed") Integer atsScore,
		Instant updatedAt) {
}
