package com.learning.resumemaker.model;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/** The file types a resume can be downloaded as. */
@Getter
@RequiredArgsConstructor
public enum ExportFormat {

	/** The template compiled to PDF. */
	PDF("pdf", "application/pdf"),
	/** The filled template's LaTeX source. */
	TEX("tex", "application/x-tex");

	private final String extension;
	private final String contentType;
}
