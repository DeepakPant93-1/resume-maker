package com.learning.resumemaker.model;

/**
 * A resume rendered into a downloadable file.
 *
 * @param fileName    file name to offer the browser, e.g. "Jane_Doe_Resume.tex"
 * @param contentType media type of the content
 * @param content     the file's bytes
 */
public record ResumeFile(String fileName, String contentType, byte[] content) {
}
