package com.learning.resumemaker.service;

import java.nio.charset.StandardCharsets;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.model.ExportFormat;
import com.learning.resumemaker.model.ResumeFile;
import com.learning.resumemaker.repository.ResumeRepository;
import com.learning.resumemaker.security.UserContext;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Turns one of the signed-in user's resumes into a downloadable file (PDF or LaTeX) in the template they chose. */
@Slf4j
@RequiredArgsConstructor
@Service
public class ResumeExportService {

	private final ResumeRepository repository;
	private final ResumeTemplateService templateService;
	private final LatexCompiler latexCompiler;

	/**
	 * Renders a resume into a template.
	 *
	 * @param id         id of the user's resume
	 * @param templateId id of the template, e.g. "classic"
	 * @param format     PDF (the template compiled) or TEX (its LaTeX source)
	 * @return the file
	 * @throws ResumeNotFoundException if the user has no such resume
	 * @throws com.learning.resumemaker.exception.TemplateNotFoundException if there is no such template
	 * @throws com.learning.resumemaker.exception.LatexUnavailableException if a PDF is asked for and no LaTeX
	 *                                                                      engine is installed
	 */
	public ResumeFile exportResume(String id, String templateId, ExportFormat format) {
		ResumeDocument resume = repository.findByIdAndUserId(id, UserContext.requireUserId())
				.orElseThrow(() -> new ResumeNotFoundException(id));
		String latex = templateService.renderTemplate(templateId, resume);
		byte[] content = format == ExportFormat.PDF ? latexCompiler.compileToPdf(latex)
				: latex.getBytes(StandardCharsets.UTF_8);
		log.info("Resume {} exported as {} with template {}", id, format, templateId);
		return new ResumeFile(fileStem(resume) + "." + format.getExtension(), format.getContentType(), content);
	}

	/** A safe file name without extension, e.g. "Jane_Doe_Resume"; "Resume" when the name is empty. */
	private static String fileStem(ResumeDocument resume) {
		String name = resume.getProfile() == null ? null : resume.getProfile().getFullName();
		String safe = name == null ? "" : name.replaceAll("[^A-Za-z0-9]+", "_").replaceAll("^_+|_+$", "");
		return safe.isEmpty() ? "Resume" : safe + "_Resume";
	}
}
