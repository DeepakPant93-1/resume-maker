package com.learning.resumemaker.exception;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Map;

import org.junit.jupiter.api.Test;

import feign.FeignException;
import feign.Request;
import feign.Request.HttpMethod;
import feign.Response;
import feign.RetryableException;

/** Every failure becomes the one error body, with the right status. */
class GlobalExceptionHandlerTest {

	private final GlobalExceptionHandler handler = new GlobalExceptionHandler(
			Clock.fixed(Instant.parse("2026-10-06T10:00:00Z"), ZoneOffset.UTC));
	private final Request request = Request.create(HttpMethod.POST, "http://agent/api/ats", Map.of(), null,
			StandardCharsets.UTF_8, null);

	@Test
	void anApplicationExceptionKeepsItsStatusAndMessage() {
		var result = handler.handleBase(new ResumeNotFoundException("r1"));

		assertThat(result.getStatusCode().value()).isEqualTo(404);
		assertThat(result.getBody().message()).isEqualTo("Resume not found: r1");
		assertThat(result.getBody().status()).isEqualTo(404);
	}

	@Test
	void aClientErrorFromTheAgentKeepsItsStatusAndDetailText() {
		Response response = Response.builder().status(409).reason("Conflict").request(request).headers(Map.of())
				.body("{\"detail\":\"Not allowed\"}", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#atsScore", response));

		assertThat(result.getStatusCode().value()).isEqualTo(409);
		assertThat(result.getBody().message()).isEqualTo("Not allowed");
	}

	@Test
	void aClientErrorWithoutADetailFieldIsShownAsIs() {
		Response response = Response.builder().status(400).reason("Bad Request").request(request).headers(Map.of())
				.body("plain text", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#atsScore", response));

		assertThat(result.getBody().message()).isEqualTo("Agent service: plain text");
	}

	@Test
	void anUnreachableAgentIsServiceUnavailable() {
		var refused = new RetryableException(-1, "Connection refused", HttpMethod.POST, new IOException("refused"),
				(Long) null, request);

		assertThat(handler.handleAgentFailure(refused).getStatusCode().value()).isEqualTo(503);
	}

	@Test
	void aServerErrorFromTheAgentIsABadGateway() {
		Response response = Response.builder().status(500).reason("Server Error").request(request).headers(Map.of())
				.body("boom", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#atsScore", response));

		assertThat(result.getStatusCode().value()).isEqualTo(502);
	}

	@Test
	void anUnexpectedErrorIsAGenericInternalServerError() {
		var result = handler.handleUnexpected(new IllegalStateException("secret internals"));

		assertThat(result.getStatusCode().value()).isEqualTo(500);
		assertThat(result.getBody().message()).doesNotContain("secret");
	}
}
