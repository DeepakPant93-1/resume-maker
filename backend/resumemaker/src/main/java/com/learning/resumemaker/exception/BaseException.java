package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

import lombok.Getter;

/** Parent of every custom exception of the application; carries the HTTP status the client should get. */
@Getter
public abstract class BaseException extends RuntimeException {

	private final HttpStatus status;

	/**
	 * Creates an exception with a client-safe message.
	 *
	 * @param status  HTTP status to answer with
	 * @param message message shown to the client
	 */
	protected BaseException(HttpStatus status, String message) {
		super(message);
		this.status = status;
	}

	/**
	 * Creates an exception that wraps an underlying cause.
	 *
	 * @param status  HTTP status to answer with
	 * @param message message shown to the client
	 * @param cause   the underlying failure
	 */
	protected BaseException(HttpStatus status, String message, Throwable cause) {
		super(message, cause);
		this.status = status;
	}
}
