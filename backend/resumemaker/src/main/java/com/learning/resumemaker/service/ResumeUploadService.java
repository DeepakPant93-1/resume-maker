package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.InputStream;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.learning.resumemaker.exception.InvalidResumeFileException;
import com.learning.resumemaker.model.ResumeResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class ResumeUploadService {

	private final ResumeParser parser;
	private final ResumeService resumeService;

	/** PDF to JSON to database. An AI run is started separately, see RunService. */
	public ResumeResponse upload(String userId, MultipartFile file) {
		if (file == null || file.isEmpty()) {
			log.warn("Upload rejected: no file or empty file");
			throw new InvalidResumeFileException("No file uploaded");
		}
		String name = file.getOriginalFilename();
		if (name == null || !name.toLowerCase().endsWith(".pdf")) {
			log.warn("Upload rejected: '{}' is not a PDF", name);
			throw new InvalidResumeFileException("Only PDF files are supported");
		}
		try (InputStream in = file.getInputStream()) {
			log.info("Parsing '{}'", name);
			ResumeResponse saved = resumeService.create(userId, parser.parse(in));
			log.info("Saved parsed resume to database, resumeId={}", saved.getId());
			return saved;
		} catch (IOException e) {
			log.error("Could not read uploaded file '{}'", name, e);
			throw new InvalidResumeFileException("Could not read the uploaded file", e);
		}
	}
}
