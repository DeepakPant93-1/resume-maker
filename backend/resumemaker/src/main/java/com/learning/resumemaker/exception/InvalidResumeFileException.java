package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when an uploaded resume file is missing, is not a PDF or cannot be read. */
public class InvalidResumeFileException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param message message shown to the client
	 */
	public InvalidResumeFileException(String message) {
		super(HttpStatus.BAD_REQUEST, message);
	}

	/**
	 * Creates the exception with the failure that caused it.
	 *
	 * @param message message shown to the client
	 * @param cause   the underlying failure
	 */
	public InvalidResumeFileException(String message, Throwable cause) {
		super(HttpStatus.BAD_REQUEST, message, cause);
	}
}
