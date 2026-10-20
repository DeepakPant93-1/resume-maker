package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when a job application does not exist or belongs to another user. */
public class ApplicationNotFoundException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param id id of the application that was asked for
	 */
	public ApplicationNotFoundException(String id) {
		super(HttpStatus.NOT_FOUND, "Application not found: " + id);
	}
}
