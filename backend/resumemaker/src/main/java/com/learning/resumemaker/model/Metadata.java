package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Resume title, template and the ATS score of the last save. */
@Builder
@Schema(description = "Resume title, template and ATS score")
public record Metadata(
		@Size(max = 200) String title,
		@Size(max = 100) String template,
		@Schema(description = "Computed by the server on every save; a value sent by the client is ignored", accessMode = Schema.AccessMode.READ_ONLY) Integer atsScore) {
}
