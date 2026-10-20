package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when a download asks for a resume template that does not exist. */
public class TemplateNotFoundException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param id id of the template that was asked for
	 */
	public TemplateNotFoundException(String id) {
		super(HttpStatus.NOT_FOUND, "Template not found: " + id);
	}
}
