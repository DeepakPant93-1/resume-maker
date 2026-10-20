package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;

/** One LaTeX template a resume can be downloaded in. */
@Schema(description = "A LaTeX resume template")
public record ResumeTemplate(
		@Schema(description = "Value to pass as the download's template parameter", example = "classic") String id,
		@Schema(description = "Name to show the user", example = "Classic") String name) {
}
