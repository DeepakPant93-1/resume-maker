package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Locale;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.exception.InvalidResumeFileException;
import com.learning.resumemaker.model.ParseRequest;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Turns an uploaded PDF into a stored resume: Java reads the text, the agent service structures it. */
@Slf4j
@Service
@RequiredArgsConstructor
public class ResumeUploadService {

	private final PdfTextExtractor extractor;
	private final AgentClient agentClient;
	private final ResumeService resumeService;

	/**
	 * Extracts the text of the PDF, has the agent service map it into a resume, and saves that as a new resume of
	 * the signed-in user.
	 *
	 * @param file the uploaded PDF
	 * @return the saved resume
	 * @throws InvalidResumeFileException if the file is missing, not a PDF, unreadable, or has no text
	 */
	public ResumeResponse uploadResume(MultipartFile file) {
		if (file == null || file.isEmpty()) {
			throw new InvalidResumeFileException("No file uploaded");
		}
		String name = file.getOriginalFilename();
		if (name == null || !name.toLowerCase(Locale.ROOT).endsWith(".pdf")) {
			throw new InvalidResumeFileException("Only PDF files are supported");
		}
		String text;
		try (InputStream in = file.getInputStream()) {
			log.info("Reading '{}' ({} bytes)", name, file.getSize());
			text = extractor.extract(in);
		} catch (IOException e) {
			throw new InvalidResumeFileException("Could not read the uploaded file", e);
		}
		if (text.isBlank()) {
			throw new InvalidResumeFileException("The PDF has no readable text (is it a scan?)");
		}
		ResumeRequest parsed = agentClient.parseResume(ParseRequest.builder().text(text).build());
		ResumeResponse saved = resumeService.createResume(parsed);
		log.info("Saved parsed resume {}", saved.id());
		return saved;
	}
}
