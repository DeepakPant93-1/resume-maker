package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** A language the person speaks and how well. */
@Builder
@Schema(description = "One spoken language")
public record SpokenLanguage(
		@Size(max = 100) String language,
		@Size(max = 50) String proficiency) {
}
