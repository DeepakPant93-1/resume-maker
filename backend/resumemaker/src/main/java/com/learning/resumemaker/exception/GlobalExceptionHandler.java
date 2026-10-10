package com.learning.resumemaker.exception;

import java.time.Clock;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import com.learning.resumemaker.model.ErrorResponse;
import com.learning.resumemaker.web.RequestContextInterceptor;

import feign.FeignException;
import jakarta.validation.ConstraintViolationException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpMediaTypeNotSupportedException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.multipart.support.MissingServletRequestPartException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

/**
 * Turns every failure into one error body. Each exception is logged here and only here; a stack trace is printed
 * for server errors (5xx) only.
 */
@Slf4j
@RestControllerAdvice
@RequiredArgsConstructor
public class GlobalExceptionHandler {

	private static final Pattern DETAIL = Pattern.compile("\"detail\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");

	private final Clock clock;

	/** Handles the application's own exceptions using the status each one carries. */
	@ExceptionHandler(BaseException.class)
	public ResponseEntity<ErrorResponse> handleBase(BaseException ex) {
		log.warn("Request failed: {}", ex.getMessage());
		return respond(ex.getStatus(), ex.getMessage(), null);
	}

	/** Handles request bodies that fail bean validation, listing every invalid field. */
	@ExceptionHandler(MethodArgumentNotValidException.class)
	public ResponseEntity<ErrorResponse> handleInvalidBody(MethodArgumentNotValidException ex) {
		List<ErrorResponse.FieldProblem> problems = ex.getBindingResult().getFieldErrors().stream()
				.map(error -> new ErrorResponse.FieldProblem(error.getField(), error.getDefaultMessage())).toList();
		log.warn("Request validation failed for {} field(s)", problems.size());
		return respond(HttpStatus.BAD_REQUEST, "The request is not valid", problems);
	}

	/** Handles invalid path or query values. */
	@ExceptionHandler(ConstraintViolationException.class)
	public ResponseEntity<ErrorResponse> handleConstraintViolation(ConstraintViolationException ex) {
		List<ErrorResponse.FieldProblem> problems = ex.getConstraintViolations().stream()
				.map(v -> new ErrorResponse.FieldProblem(v.getPropertyPath().toString(), v.getMessage())).toList();
		log.warn("Request validation failed for {} value(s)", problems.size());
		return respond(HttpStatus.BAD_REQUEST, "The request is not valid", problems);
	}

	/** Handles malformed JSON and missing or unsupported request parts. */
	@ExceptionHandler({ HttpMessageNotReadableException.class, MissingServletRequestPartException.class,
			HttpMediaTypeNotSupportedException.class, HttpRequestMethodNotSupportedException.class })
	public ResponseEntity<ErrorResponse> handleMalformedRequest(Exception ex) {
		HttpStatus status = ex instanceof HttpMediaTypeNotSupportedException ? HttpStatus.UNSUPPORTED_MEDIA_TYPE
				: ex instanceof HttpRequestMethodNotSupportedException ? HttpStatus.METHOD_NOT_ALLOWED
				: HttpStatus.BAD_REQUEST;
		log.warn("Malformed request: {}", ex.getClass().getSimpleName());
		return respond(status, "The request could not be read", null);
	}

	/** Handles uploads larger than the configured limit. */
	@ExceptionHandler(MaxUploadSizeExceededException.class)
	public ResponseEntity<ErrorResponse> handleTooLarge(MaxUploadSizeExceededException ex) {
		log.warn("Upload rejected: file too large");
		return respond(HttpStatus.CONTENT_TOO_LARGE, "The uploaded file is too large", null);
	}

	/** Handles URLs that match nothing. */
	@ExceptionHandler(NoResourceFoundException.class)
	public ResponseEntity<ErrorResponse> handleNoResource(NoResourceFoundException ex) {
		log.warn("No resource: {}", ex.getResourcePath());
		return respond(HttpStatus.NOT_FOUND, "Not found", null);
	}

	/**
	 * Handles failures of calls to the agent service. A 4xx is passed on with its status; no response at all
	 * (connection refused or timeout) is 503; anything else is 502.
	 */
	@ExceptionHandler(FeignException.class)
	public ResponseEntity<ErrorResponse> handleAgentFailure(FeignException ex) {
		int status = ex.status();
		if (status >= 400 && status < 500) {
			log.warn("Agent service rejected the request: HTTP {}", status);
			return respond(HttpStatus.valueOf(status), detailOf(ex.contentUTF8()), null);
		}
		if (status < 0) {
			log.error("Agent service unreachable", ex);
			return respond(HttpStatus.SERVICE_UNAVAILABLE, "The AI agent service is not reachable", null);
		}
		log.error("Agent service failed with HTTP {}", status, ex);
		return respond(HttpStatus.BAD_GATEWAY, "The AI agent service returned an error", null);
	}

	/** Fallback for anything unexpected: a generic message for the client, the full stack trace in the log. */
	@ExceptionHandler(Exception.class)
	public ResponseEntity<ErrorResponse> handleUnexpected(Exception ex) {
		log.error("Unexpected error", ex);
		return respond(HttpStatus.INTERNAL_SERVER_ERROR, "Something went wrong", null);
	}

	/** The agent service reports errors as {"detail": "..."}; returns just the text, or the raw body if it is not that shape. */
	private static String detailOf(String body) {
		Matcher detail = DETAIL.matcher(body == null ? "" : body);
		return detail.find() ? detail.group(1).replace("\\\"", "\"") : "Agent service: " + body;
	}

	private ResponseEntity<ErrorResponse> respond(HttpStatus status, String message,
			List<ErrorResponse.FieldProblem> problems) {
		ErrorResponse body = ErrorResponse.builder().message(message).status(status.value()).timestamp(clock.instant())
				.requestId(MDC.get(RequestContextInterceptor.REQUEST_ID_KEY)).errors(problems).build();
		return ResponseEntity.status(status).body(body);
	}
}
