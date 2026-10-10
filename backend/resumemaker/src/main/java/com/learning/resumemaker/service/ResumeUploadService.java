package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Locale;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.learning.resumemaker.exception.InvalidResumeFileException;
import com.learning.resumemaker.model.ResumeResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Turns an uploaded PDF into a stored resume. */
@Slf4j
@Service
@RequiredArgsConstructor
public class ResumeUploadService {

	private final ResumeParser parser;
	private final ResumeService resumeService;

	/**
	 * Parses the PDF and saves the result as a new resume of the signed-in user.
	 *
	 * @param file the uploaded PDF
	 * @return the saved resume
	 * @throws InvalidResumeFileException if the file is missing, not a PDF or unreadable
	 */
	public ResumeResponse uploadResume(MultipartFile file) {
		if (file == null || file.isEmpty()) {
			throw new InvalidResumeFileException("No file uploaded");
		}
		String name = file.getOriginalFilename();
		if (name == null || !name.toLowerCase(Locale.ROOT).endsWith(".pdf")) {
			throw new InvalidResumeFileException("Only PDF files are supported");
		}
		try (InputStream in = file.getInputStream()) {
			log.info("Parsing '{}' ({} bytes)", name, file.getSize());
			ResumeResponse saved = resumeService.createResume(parser.parse(in));
			log.info("Saved parsed resume {}", saved.id());
			return saved;
		} catch (IOException e) {
			throw new InvalidResumeFileException("Could not read the uploaded file", e);
		}
	}
}
