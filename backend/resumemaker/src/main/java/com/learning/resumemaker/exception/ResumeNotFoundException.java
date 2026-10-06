package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.NOT_FOUND)
public class ResumeNotFoundException extends RuntimeException {

	public ResumeNotFoundException(String id) {
		super("Resume not found: " + id);
	}
}
