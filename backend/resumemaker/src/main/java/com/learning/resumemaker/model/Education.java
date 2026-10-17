package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** One degree or course of study. */
@Builder
@Schema(description = "One education entry")
public record Education(
		@Size(max = 200) String degree,
		@Size(max = 200) String university,
		@Size(max = 20) String startYear,
		@Size(max = 20) String endYear,
		@Size(max = 50) String grade,
		@Size(max = 200) String location) {
}
