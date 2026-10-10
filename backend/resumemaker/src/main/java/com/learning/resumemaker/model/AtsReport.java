package com.learning.resumemaker.model;

import java.util.List;
import java.util.Map;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** ATS score out of 100 with its parts and suggestions, as computed by the agent service. */
@Builder
@Schema(description = "ATS score out of 100 with its parts and suggestions")
public record AtsReport(
		Integer score,
		boolean againstJob,
		Map<String, AtsComponent> components,
		List<String> suggestions) {
}
