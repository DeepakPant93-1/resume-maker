package com.learning.resumemaker.service;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.stereotype.Service;

import com.learning.resumemaker.config.LatexProperties;
import com.learning.resumemaker.exception.LatexUnavailableException;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Compiles LaTeX source to PDF with pdflatex, in a temporary folder that is deleted afterwards.
 * <p>
 * pdflatex runs without shell escape and without halting on errors: a character the fonts cannot draw (e.g.
 * Devanagari) is dropped with a warning instead of failing the whole download. Only a run that writes no PDF fails.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@EnableConfigurationProperties(LatexProperties.class)
public class LatexCompiler {

	private static final String SOURCE = "resume.tex";
	private static final String OUTPUT = "resume.pdf";
	private static final String LOG = "resume.log";

	private final LatexProperties properties;

	/**
	 * Compiles one LaTeX document.
	 *
	 * @param latex the complete document source
	 * @return the bytes of the PDF
	 * @throws LatexUnavailableException if the LaTeX command cannot be started
	 */
	public byte[] compileToPdf(String latex) {
		Path dir = createWorkDir();
		try {
			Files.writeString(dir.resolve(SOURCE), latex, StandardCharsets.UTF_8);
			int exitCode = runLatex(dir);
			Path pdf = dir.resolve(OUTPUT);
			if (!Files.exists(pdf)) {
				throw new IllegalStateException("LaTeX produced no PDF (exit code " + exitCode + "): " + firstError(dir));
			}
			if (exitCode != 0) {
				log.warn("LaTeX reported errors, the PDF may miss some characters: {}", firstError(dir));
			}
			return Files.readAllBytes(pdf);
		} catch (IOException ex) {
			throw new UncheckedIOException("Could not compile the resume to PDF", ex);
		} finally {
			deleteWorkDir(dir);
		}
	}

	/** Runs pdflatex on the source in {@code dir} and returns its exit code. */
	private int runLatex(Path dir) throws IOException {
		Process process;
		try {
			process = new ProcessBuilder(properties.command(), "-no-shell-escape", "-interaction=nonstopmode", SOURCE)
					.directory(dir.toFile())
					.redirectErrorStream(true)
					.redirectOutput(dir.resolve("console.txt").toFile())
					.start();
		} catch (IOException ex) {
			throw new LatexUnavailableException(properties.command());
		}
		try {
			if (!process.waitFor(properties.timeout().toMillis(), TimeUnit.MILLISECONDS)) {
				process.destroyForcibly();
				throw new IllegalStateException("LaTeX did not finish within " + properties.timeout());
			}
			return process.exitValue();
		} catch (InterruptedException ex) {
			process.destroyForcibly();
			Thread.currentThread().interrupt();
			throw new IllegalStateException("Interrupted while compiling LaTeX", ex);
		}
	}

	/** The first error line ("! ...") of the LaTeX log, without the document text around it. */
	private static String firstError(Path dir) {
		try (Stream<String> lines = Files.lines(dir.resolve(LOG), StandardCharsets.UTF_8)) {
			return lines.filter(line -> line.startsWith("!")).findFirst().orElse("no error in the log");
		} catch (IOException | UncheckedIOException ex) {
			return "no log";
		}
	}

	private static Path createWorkDir() {
		try {
			return Files.createTempDirectory("resume-latex-");
		} catch (IOException ex) {
			throw new UncheckedIOException("Could not create a folder to compile LaTeX in", ex);
		}
	}

	/** Deletes the work folder and everything LaTeX wrote into it; a leftover file is only logged. */
	private static void deleteWorkDir(Path dir) {
		try (Stream<Path> paths = Files.walk(dir)) {
			paths.sorted(Comparator.reverseOrder()).forEach(path -> path.toFile().delete());
		} catch (IOException ex) {
			log.warn("Could not delete LaTeX work folder {}", dir);
		}
	}
}
