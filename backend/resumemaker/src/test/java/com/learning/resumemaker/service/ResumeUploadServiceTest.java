package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.exception.InvalidResumeFileException;
import com.learning.resumemaker.model.ParseRequest;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.SpokenLanguage;

@ExtendWith(MockitoExtension.class)
class ResumeUploadServiceTest {

	@Mock
	PdfTextExtractor extractor;
	@Mock
	AgentClient agentClient;
	@Mock
	ResumeService resumeService;

	private ResumeUploadService service() {
		return new ResumeUploadService(extractor, agentClient, resumeService);
	}

	private MockMultipartFile pdf() {
		return new MockMultipartFile("file", "cv.pdf", "application/pdf", new byte[] { 1 });
	}

	@Test
	void sendsTheExtractedTextToTheAgentAndSavesWhatItReturns() {
		ResumeRequest parsed = ResumeRequest.builder().profile(Profile.builder().fullName("Asha Rao").build())
				.spokenLanguages(List.of(new SpokenLanguage("English", "Fluent"))).build();
		ResumeResponse saved = ResumeResponse.builder().id("r1").build();
		when(extractor.extract(any())).thenReturn("Asha Rao\nJava Developer");
		when(agentClient.parseResume(any())).thenReturn(parsed);
		when(resumeService.createResume(parsed)).thenReturn(saved);

		assertThat(service().uploadResume(pdf())).isSameAs(saved);

		ArgumentCaptor<ParseRequest> sent = ArgumentCaptor.forClass(ParseRequest.class);
		verify(agentClient).parseResume(sent.capture());
		assertThat(sent.getValue().text()).isEqualTo("Asha Rao\nJava Developer");
	}

	@Test
	void aPdfWithoutTextIsRejectedWithoutCallingTheAgent() {
		when(extractor.extract(any())).thenReturn("  \n ");

		assertThatThrownBy(() -> service().uploadResume(pdf())).isInstanceOf(InvalidResumeFileException.class)
				.hasMessageContaining("no readable text");
		verify(agentClient, never()).parseResume(any());
	}

	@Test
	void aNonPdfIsRejected() {
		MockMultipartFile doc = new MockMultipartFile("file", "cv.docx", "application/msword", new byte[] { 1 });

		assertThatThrownBy(() -> service().uploadResume(doc)).isInstanceOf(InvalidResumeFileException.class);
	}
}
