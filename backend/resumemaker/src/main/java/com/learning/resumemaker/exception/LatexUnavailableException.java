package com.learning.resumemaker.exception;

import org.springframework.http.HttpStatus;

/** Thrown when a PDF is asked for but no LaTeX engine is installed on the server. */
public class LatexUnavailableException extends BaseException {

	/**
	 * Creates the exception.
	 *
	 * @param command the LaTeX command that could not be started
	 */
	public LatexUnavailableException(String command) {
		super(HttpStatus.SERVICE_UNAVAILABLE,
				"PDF download is not available: the server has no LaTeX engine (" + command + ")");
	}
}
