package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when a resume does not exist or belongs to another user. */
public class ResumeNotFoundException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param id id of the resume that was asked for
	 */
	public ResumeNotFoundException(String id) {
		super(HttpStatus.NOT_FOUND, "Resume not found: " + id);
	}
}
