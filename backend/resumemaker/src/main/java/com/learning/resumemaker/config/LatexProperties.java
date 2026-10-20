package com.learning.resumemaker.config;

import java.time.Duration;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Settings for turning LaTeX into PDF.
 *
 * @param command the pdflatex executable, a name on the PATH or a full path
 * @param timeout how long one compile may take before it is stopped
 */
@ConfigurationProperties(prefix = "app.latex")
public record LatexProperties(String command, Duration timeout) {
}
