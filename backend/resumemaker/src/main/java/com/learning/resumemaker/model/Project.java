package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** One project on the resume. */
@Builder(toBuilder = true)
@Schema(description = "One project entry")
public record Project(
		@Size(max = 200) String name,
		@Size(max = 5000) String description,
		@Size(max = 500) String technologies) {
}
