package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when a request breaks a business rule that bean validation cannot express. */
public class InvalidRequestException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param message message shown to the client
	 */
	public InvalidRequestException(String message) {
		super(HttpStatus.BAD_REQUEST, message);
	}
}
