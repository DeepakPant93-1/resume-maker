package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;
import org.junit.jupiter.api.Test;

import com.learning.resumemaker.exception.InvalidResumeFileException;

class PdfTextExtractorTest {

	private final PdfTextExtractor extractor = new PdfTextExtractor();

	@Test
	void returnsTheTextOfThePdfUnchanged() throws Exception {
		ByteArrayOutputStream out = new ByteArrayOutputStream();
		try (PDDocument document = new PDDocument()) {
			PDPage page = new PDPage();
			document.addPage(page);
			try (PDPageContentStream stream = new PDPageContentStream(document, page)) {
				stream.beginText();
				stream.setFont(new PDType1Font(Standard14Fonts.FontName.HELVETICA), 12);
				stream.newLineAtOffset(50, 700);
				stream.showText("Asha Rao - Java Developer");
				stream.endText();
			}
			document.save(out);
		}

		assertThat(extractor.extract(new ByteArrayInputStream(out.toByteArray()))).contains("Asha Rao - Java Developer");
	}

	@Test
	void aFileThatIsNotAPdfIsRejected() {
		assertThatThrownBy(() -> extractor.extract(new ByteArrayInputStream("hello".getBytes())))
				.isInstanceOf(InvalidResumeFileException.class);
	}
}
