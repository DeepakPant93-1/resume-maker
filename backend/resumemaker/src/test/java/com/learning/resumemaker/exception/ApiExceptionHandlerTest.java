package com.learning.resumemaker.exception;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

import org.junit.jupiter.api.Test;

import feign.FeignException;
import feign.Request;
import feign.Request.HttpMethod;
import feign.Response;
import feign.RetryableException;

class ApiExceptionHandlerTest {

	private final ApiExceptionHandler handler = new ApiExceptionHandler();
	private final Request request = Request.create(HttpMethod.POST, "http://agent/api/runs/x/resume", Map.of(), null,
			StandardCharsets.UTF_8, null);

	@Test
	void aClientErrorFromTheAgentKeepsItsStatusAndMessage() {
		Response response = Response.builder().status(409).reason("Conflict").request(request).headers(Map.of())
				.body("{\"detail\":\"Run is 'completed', not waiting for an answer\"}", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#answerRun", response));

		assertThat(result.getStatusCode().value()).isEqualTo(409);
		// just the agent's detail text, not the raw JSON body
		assertThat(result.getBody().get("message")).isEqualTo("Run is 'completed', not waiting for an answer");
	}

	@Test
	void aClientErrorWithoutADetailFieldIsShownAsIs() {
		Response response = Response.builder().status(400).reason("Bad Request").request(request).headers(Map.of())
				.body("plain text", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#startRun", response));

		assertThat(result.getBody().get("message")).isEqualTo("Agent service: plain text");
	}

	@Test
	void anUnreachableAgentIsServiceUnavailable() {
		var refused = new RetryableException(-1, "Connection refused", HttpMethod.POST, new IOException("refused"),
				(Long) null, request);

		var result = handler.handleAgentFailure(refused);

		assertThat(result.getStatusCode().value()).isEqualTo(503);
		assertThat(result.getBody().get("message")).contains("not reachable");
	}

	@Test
	void aServerErrorFromTheAgentIsABadGateway() {
		Response response = Response.builder().status(500).reason("Server Error").request(request).headers(Map.of())
				.body("boom", StandardCharsets.UTF_8).build();

		var result = handler.handleAgentFailure(FeignException.errorStatus("AgentClient#getRun", response));

		assertThat(result.getStatusCode().value()).isEqualTo(502);
	}
}
