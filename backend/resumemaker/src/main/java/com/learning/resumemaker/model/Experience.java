package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** One job on the resume. */
@Builder
@Schema(description = "One work experience entry")
public record Experience(
		@Size(max = 200) String jobTitle,
		@Size(max = 200) String company,
		@Size(max = 50) String startDate,
		@Size(max = 50) String endDate,
		boolean current,
		@Size(max = 10000) String achievements) {
}
