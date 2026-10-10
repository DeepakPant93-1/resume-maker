package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;

@ExtendWith(MockitoExtension.class)
class SummaryServiceTest {

	@Mock
	AgentClient agentClient;

	private ResumeRequest resume() {
		return ResumeRequest.builder().profile(Profile.builder().fullName("Suraj").jobTitle("Java Developer").build())
				.build();
	}

	@Test
	void sendsTheResumeAndReturnsTheWrittenSummary() {
		when(agentClient.writeSummary(any())).thenReturn(new SummaryResponse("Java developer."));
		ResumeRequest resume = resume();

		SummaryResponse response = new SummaryService(agentClient).writeSummary(new SummaryRequest(resume, "old text"));

		assertThat(response.summary()).isEqualTo("Java developer.");
		ArgumentCaptor<SummaryRequest> sent = ArgumentCaptor.forClass(SummaryRequest.class);
		verify(agentClient).writeSummary(sent.capture());
		assertThat(sent.getValue().resume()).isSameAs(resume);
		assertThat(sent.getValue().summary()).isEqualTo("old text");
	}

	@Test
	void aBlankSummaryIsSentAsNullSoTheAgentWritesANewOne() {
		when(agentClient.writeSummary(any())).thenReturn(new SummaryResponse("Java developer."));

		new SummaryService(agentClient).writeSummary(new SummaryRequest(resume(), "   "));

		ArgumentCaptor<SummaryRequest> sent = ArgumentCaptor.forClass(SummaryRequest.class);
		verify(agentClient).writeSummary(sent.capture());
		assertThat(sent.getValue().summary()).isNull();
	}
}
