package com.learning.resumemaker.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** One part of the ATS score. Which detail fields are filled depends on the part (keywords, completeness, impact, readability). */
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "One part of the ATS score")
public record AtsComponent(
		Double points,
		Integer max,
		List<String> matched,
		List<String> missing,
		Integer bullets,
		Integer withNumbers,
		Integer longBullets,
		Integer summaryWords) {
}
