package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** The professional summary written by the agent service. */
@Builder
@Schema(description = "A written professional summary")
public record SummaryResponse(String summary) {
}
