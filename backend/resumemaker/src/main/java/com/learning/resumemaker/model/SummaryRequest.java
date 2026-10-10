package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/**
 * The resume as the editor has it, plus the summary typed so far (blank means write a new one).
 * It is the body of both the UI's call and the call on to the agent service.
 */
@Builder
@Schema(description = "The resume being edited and the summary typed so far")
public record SummaryRequest(
		@NotNull(message = "A resume is required") @Valid ResumeRequest resume,
		@Size(max = 5000) String summary) {
}
