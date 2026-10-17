package com.learning.resumemaker.model;

import java.time.Instant;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** Error body returned for every failed request. */
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Error returned for every failed request")
public record ErrorResponse(
		@Schema(description = "Human readable reason") String message,
		@Schema(description = "HTTP status code") int status,
		@Schema(description = "Moment the error happened") Instant timestamp,
		@Schema(description = "Id of the failed request, same as the response-id header") String requestId,
		@Schema(description = "Per-field problems, only for validation errors") List<FieldProblem> errors) {

	/** One invalid field of a request body. */
	@Schema(description = "One invalid field")
	public record FieldProblem(String field, String message) {
	}
}
