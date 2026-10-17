package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.InputStream;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;

import com.learning.resumemaker.exception.InvalidResumeFileException;

import lombok.extern.slf4j.Slf4j;

/** Reads the raw text out of a PDF. It does no parsing: turning the text into a resume is the agent service's job. */
@Slf4j
@Component
public class PdfTextExtractor {

	/**
	 * Extracts the text of every page.
	 *
	 * @param pdf the PDF bytes
	 * @return the text, exactly as PDFBox reads it
	 * @throws InvalidResumeFileException if the PDF cannot be read
	 */
	public String extract(InputStream pdf) {
		try (PDDocument document = Loader.loadPDF(pdf.readAllBytes())) {
			String text = new PDFTextStripper().getText(document);
			log.info("Extracted {} characters from {} PDF page(s)", text.length(), document.getNumberOfPages());
			return text;
		} catch (IOException e) {
			throw new InvalidResumeFileException("Could not read the PDF file", e);
		}
	}
}
