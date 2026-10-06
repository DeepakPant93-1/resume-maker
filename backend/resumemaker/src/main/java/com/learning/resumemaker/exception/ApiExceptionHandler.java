package com.learning.resumemaker.exception;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import feign.FeignException;
import lombok.extern.slf4j.Slf4j;

/** Turns failures of calls to the agent service into clean HTTP responses for the UI. */
@Slf4j
@RestControllerAdvice
public class ApiExceptionHandler {

	private static final Pattern DETAIL = Pattern.compile("\"detail\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");

	/**
	 * A 4xx from the agent service (unknown run, run not waiting for an answer...) is passed on with its status.
	 * No response at all (status -1: connection refused or timeout) is 503; anything else is 502.
	 */
	@ExceptionHandler(FeignException.class)
	public ResponseEntity<Map<String, String>> handleAgentFailure(FeignException e) {
		int status = e.status();
		if (status >= 400 && status < 500) {
			log.warn("Agent service rejected the request: HTTP {} {}", status, e.contentUTF8());
			return ResponseEntity.status(status).body(Map.of("message", detailOf(e.contentUTF8())));
		}
		if (status < 0) {
			log.error("Agent service unreachable: {}", e.getMessage());
			return ResponseEntity.status(503).body(Map.of("message", "The AI agent service is not reachable"));
		}
		log.error("Agent service failed: HTTP {} {}", status, e.contentUTF8());
		return ResponseEntity.status(502).body(Map.of("message", "The AI agent service returned an error"));
	}

	/** The agent service reports errors as {"detail": "..."}; show just the text, or the raw body if it is not that shape. */
	private static String detailOf(String body) {
		Matcher detail = DETAIL.matcher(body == null ? "" : body);
		return detail.find() ? detail.group(1).replace("\\\"", "\"") : "Agent service: " + body;
	}
}
