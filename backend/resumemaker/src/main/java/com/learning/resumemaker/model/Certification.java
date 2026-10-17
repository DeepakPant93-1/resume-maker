package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** One certification. */
@Builder
@Schema(description = "One certification entry")
public record Certification(
		@Size(max = 200) String name,
		@Size(max = 200) String issuer) {
}
