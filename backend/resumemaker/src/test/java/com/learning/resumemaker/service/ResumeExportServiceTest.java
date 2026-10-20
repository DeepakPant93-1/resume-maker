package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.nio.charset.StandardCharsets;
import java.util.Optional;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.model.ExportFormat;
import com.learning.resumemaker.model.ResumeFile;
import com.learning.resumemaker.repository.ResumeRepository;
import com.learning.resumemaker.security.UserContext;

@ExtendWith(MockitoExtension.class)
class ResumeExportServiceTest {

	@Mock
	ResumeRepository repository;
	@Mock
	ResumeTemplateService templateService;
	@Mock
	LatexCompiler latexCompiler;

	@BeforeEach
	void signIn() {
		UserContext.setUserId("u1");
	}

	@AfterEach
	void signOut() {
		UserContext.clear();
	}

	private ResumeExportService service() {
		return new ResumeExportService(repository, templateService, latexCompiler);
	}

	private static ResumeDocument resumeOf(String fullName) {
		return ResumeDocument.builder().id("r1").userId("u1")
				.profile(ResumeDocument.Profile.builder().fullName(fullName).build()).build();
	}

	@Test
	void exportsTheUsersResumeAsPdf() {
		ResumeDocument resume = resumeOf("Jane  O'Doe");
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(resume));
		when(templateService.renderTemplate("classic", resume)).thenReturn("\\documentclass{article}");
		when(latexCompiler.compileToPdf("\\documentclass{article}")).thenReturn(new byte[] { 37, 80, 68, 70 });

		ResumeFile file = service().exportResume("r1", "classic", ExportFormat.PDF);

		assertThat(file.fileName()).isEqualTo("Jane_O_Doe_Resume.pdf");
		assertThat(file.contentType()).isEqualTo("application/pdf");
		assertThat(file.content()).containsExactly(37, 80, 68, 70);
	}

	@Test
	void exportsTheUsersResumeAsTexWithoutCompiling() {
		ResumeDocument resume = resumeOf("Jane Doe");
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(resume));
		when(templateService.renderTemplate("classic", resume)).thenReturn("\\documentclass{article}");

		ResumeFile file = service().exportResume("r1", "classic", ExportFormat.TEX);

		assertThat(file.fileName()).isEqualTo("Jane_Doe_Resume.tex");
		assertThat(file.contentType()).isEqualTo("application/x-tex");
		assertThat(new String(file.content(), StandardCharsets.UTF_8)).isEqualTo("\\documentclass{article}");
		verifyNoInteractions(latexCompiler);
	}

	@Test
	void namesTheFileResumeWhenTheNameIsMissing() {
		ResumeDocument resume = resumeOf(null);
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(resume));
		when(templateService.renderTemplate("classic", resume)).thenReturn("");

		assertThat(service().exportResume("r1", "classic", ExportFormat.TEX).fileName()).isEqualTo("Resume.tex");
	}

	@Test
	void anotherUsersResumeIsNotFound() {
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().exportResume("r1", "classic", ExportFormat.PDF))
				.isInstanceOf(ResumeNotFoundException.class);
		verify(templateService, never()).renderTemplate(any(), any());
		verifyNoInteractions(latexCompiler);
	}
}
