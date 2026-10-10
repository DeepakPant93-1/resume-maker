package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when credentials or the signed-in account are not valid. */
public class AuthenticationFailedException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param message message shown to the client
	 */
	public AuthenticationFailedException(String message) {
		super(HttpStatus.UNAUTHORIZED, message);
	}
}
