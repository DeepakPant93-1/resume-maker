package com.learning.resumemaker.security;

import java.io.IOException;
import java.time.Clock;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import com.learning.resumemaker.model.ErrorResponse;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import tools.jackson.databind.json.JsonMapper;

/** Answers calls with a missing, invalid or expired token with 401 and the standard error body. */
@Slf4j
@Component
@RequiredArgsConstructor
public class RestAuthenticationEntryPoint implements AuthenticationEntryPoint {

	private final JsonMapper jsonMapper;
	private final Clock clock;

	/** Writes the 401 response. The reason is logged; the token itself never is. */
	@Override
	public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException exception)
			throws IOException {
		log.warn("Rejected {} {}: {}", request.getMethod(), request.getRequestURI(), exception.getMessage());
		ErrorResponse body = ErrorResponse.builder()
				.message("Please log in again: the login token is missing, invalid or expired")
				.status(HttpStatus.UNAUTHORIZED.value()).timestamp(clock.instant()).build();
		response.setStatus(HttpStatus.UNAUTHORIZED.value());
		response.setContentType(MediaType.APPLICATION_JSON_VALUE);
		response.getWriter().write(jsonMapper.writeValueAsString(body));
	}
}
