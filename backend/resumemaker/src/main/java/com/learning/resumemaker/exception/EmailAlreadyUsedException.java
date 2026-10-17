package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when registering an email that already has an account. */
public class EmailAlreadyUsedException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param message message shown to the client
	 */
	public EmailAlreadyUsedException(String message) {
		super(HttpStatus.CONFLICT, message);
	}
}
