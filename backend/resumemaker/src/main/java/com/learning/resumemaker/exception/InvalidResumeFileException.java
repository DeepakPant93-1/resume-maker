package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.BAD_REQUEST)
public class InvalidResumeFileException extends RuntimeException {

	public InvalidResumeFileException(String message) {
		super(message);
	}

	public InvalidResumeFileException(String message, Throwable cause) {
		super(message, cause);
	}
}
