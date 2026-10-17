package com.learning.resumemaker.model;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Skills grouped by kind. */
@Builder
@Schema(description = "Skills grouped into languages, frameworks and tools")
public record Skills(
		@Size(max = 100) List<@Size(max = 100) String> languages,
		@Size(max = 100) List<@Size(max = 100) String> frameworks,
		@Size(max = 100) List<@Size(max = 100) String> tools) {
}
