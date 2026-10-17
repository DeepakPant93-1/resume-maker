package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.model.AtsComponent;
import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.ResumeRequest;

@ExtendWith(MockitoExtension.class)
class AtsServiceTest {

	@Mock
	AgentClient agentClient;

	private AtsService service() {
		return new AtsService(agentClient);
	}

	private ResumeRequest resume() {
		return ResumeRequest.builder().profile(Profile.builder().fullName("Suraj").build()).build();
	}

	private AtsReport report() {
		AtsComponent keywords = AtsComponent.builder().points(25.0).max(50).missing(List.of("kafka")).build();
		return AtsReport.builder().score(83).againstJob(true).components(Map.of("keywords", keywords))
				.suggestions(List.of("Add kafka")).build();
	}

	@Test
	void sendsTheResumeExactlyAsGivenWithTheJobDescriptionAndReturnsTheTypedReport() {
		when(agentClient.atsScore(any())).thenReturn(report());
		ResumeRequest resume = resume();

		AtsReport result = service().checkResume(new AtsRequest(resume, "Requirements\n- Kafka"));

		assertThat(result.score()).isEqualTo(83);
		assertThat(result.components().get("keywords").missing()).containsExactly("kafka");
		ArgumentCaptor<AtsRequest> sent = ArgumentCaptor.forClass(AtsRequest.class);
		verify(agentClient).atsScore(sent.capture());
		assertThat(sent.getValue().resume()).isSameAs(resume);
		assertThat(sent.getValue().jobDescription()).isEqualTo("Requirements\n- Kafka");
	}

	@Test
	void aBlankJobDescriptionIsSentAsNull() {
		when(agentClient.atsScore(any())).thenReturn(report());

		service().checkResume(new AtsRequest(resume(), "  "));

		ArgumentCaptor<AtsRequest> sent = ArgumentCaptor.forClass(AtsRequest.class);
		verify(agentClient).atsScore(sent.capture());
		assertThat(sent.getValue().jobDescription()).isNull();
	}
}
