package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import com.learning.resumemaker.config.LatexProperties;
import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.LatexUnavailableException;

class LatexCompilerTest {

	private static final String DOCUMENT = "\\documentclass{article}\\begin{document}Hi\\end{document}";

	@TempDir
	Path scripts;

	/** A stand-in for pdflatex: a shell script with the given body, run in the work folder. */
	private LatexCompiler compilerRunning(String body, Duration timeout) throws IOException {
		Path script = scripts.resolve("fake-latex.sh");
		Files.writeString(script, "#!/bin/sh\n" + body + "\n");
		assumeTrue(script.toFile().setExecutable(true), "cannot make a test script executable");
		return new LatexCompiler(new LatexProperties(script.toString(), timeout));
	}

	@Test
	void returnsThePdfLatexWrote() throws IOException {
		LatexCompiler compiler = compilerRunning("printf '%%PDF-fake' > resume.pdf", Duration.ofSeconds(10));

		assertThat(new String(compiler.compileToPdf(DOCUMENT), StandardCharsets.US_ASCII)).isEqualTo("%PDF-fake");
	}

	@Test
	void keepsThePdfWhenLatexReportsErrors() throws IOException {
		// e.g. a character the fonts cannot draw: pdflatex exits 1 but still writes the PDF
		LatexCompiler compiler = compilerRunning(
				"printf '! LaTeX Error: Unicode character\\n' > resume.log; printf '%%PDF-fake' > resume.pdf; exit 1",
				Duration.ofSeconds(10));

		assertThat(compiler.compileToPdf(DOCUMENT)).isNotEmpty();
	}

	@Test
	void failsWhenNoPdfIsWritten() throws IOException {
		LatexCompiler compiler = compilerRunning("printf '! Undefined control sequence.\\n' > resume.log; exit 1",
				Duration.ofSeconds(10));

		assertThatThrownBy(() -> compiler.compileToPdf(DOCUMENT)).isInstanceOf(IllegalStateException.class)
				.hasMessageContaining("! Undefined control sequence.");
	}

	@Test
	void stopsLatexAfterTheTimeout() throws IOException {
		LatexCompiler compiler = compilerRunning("sleep 10", Duration.ofMillis(300));

		assertThatThrownBy(() -> compiler.compileToPdf(DOCUMENT)).isInstanceOf(IllegalStateException.class)
				.hasMessageContaining("did not finish");
	}

	@Test
	void reportsAMissingLatexEngine() {
		LatexCompiler compiler = new LatexCompiler(new LatexProperties("no-such-pdflatex", Duration.ofSeconds(10)));

		assertThatThrownBy(() -> compiler.compileToPdf(DOCUMENT)).isInstanceOf(LatexUnavailableException.class);
	}

	@Test
	void compilesEveryTemplateWithRealPdflatex() {
		assumeTrue(pdflatexInstalled(), "pdflatex is not installed");
		ResumeDocument resume = ResumeDocument.builder()
				.profile(ResumeDocument.Profile.builder().fullName("Jane Doe").jobTitle("R&D Engineer").build())
				.build();
		ResumeTemplateService templates = new ResumeTemplateService();
		LatexCompiler compiler = new LatexCompiler(new LatexProperties("pdflatex", Duration.ofSeconds(60)));

		for (var template : templates.listTemplates()) {
			byte[] pdf = compiler.compileToPdf(templates.renderTemplate(template.id(), resume));

			assertThat(new String(pdf, 0, 5, StandardCharsets.US_ASCII)).as(template.id()).isEqualTo("%PDF-");
		}
	}

	private static boolean pdflatexInstalled() {
		try {
			return new ProcessBuilder("pdflatex", "--version").redirectErrorStream(true)
					.redirectOutput(ProcessBuilder.Redirect.DISCARD).start().waitFor() == 0;
		} catch (IOException | InterruptedException ex) {
			return false;
		}
	}
}
