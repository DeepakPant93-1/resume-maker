package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.InvalidRequestException;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.exception.RunNotFoundException;
import com.learning.resumemaker.mapper.ResumeMapper;
import com.learning.resumemaker.model.AgentRunRequest;
import com.learning.resumemaker.model.AnswerRequest;
import com.learning.resumemaker.model.RunStarted;
import com.learning.resumemaker.repository.ResumeRepository;

@ExtendWith(MockitoExtension.class)
class RunServiceTest {

	@Mock
	ResumeRepository repository;
	@Mock
	AgentClient agentClient;

	private RunService service() {
		return new RunService(repository, new ResumeMapper(), agentClient);
	}

	private ResumeDocument savedResume() {
		return ResumeDocument.builder().id("r1").userId("u1")
				.profile(ResumeDocument.Profile.builder().fullName("Suraj").build()).build();
	}

	@Test
	void startSendsTheUsersResumeAndJobDescriptionToTheAgentService() {
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(savedResume()));
		when(agentClient.startRun(any())).thenReturn(new RunStarted("run-1", "running"));

		RunStarted started = service().start("u1", "r1", "Requirements\n- Java");

		assertThat(started.getRunId()).isEqualTo("run-1");
		ArgumentCaptor<AgentRunRequest> sent = ArgumentCaptor.forClass(AgentRunRequest.class);
		verify(agentClient).startRun(sent.capture());
		assertThat(sent.getValue().getJobDescription()).isEqualTo("Requirements\n- Java");
		assertThat(sent.getValue().getResume().getId()).isEqualTo("r1");
		assertThat(sent.getValue().getResume().getProfile().getFullName()).isEqualTo("Suraj");
	}

	@Test
	void aBlankJobDescriptionIsSentAsNull() {
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(savedResume()));
		when(agentClient.startRun(any())).thenReturn(new RunStarted("run-1", "running"));

		service().start("u1", "r1", "   ");

		ArgumentCaptor<AgentRunRequest> sent = ArgumentCaptor.forClass(AgentRunRequest.class);
		verify(agentClient).startRun(sent.capture());
		assertThat(sent.getValue().getJobDescription()).isNull();
	}

	@Test
	void startFailsWithoutCallingTheAgentWhenTheResumeIsMissingOrNotTheirs() {
		when(repository.findByIdAndUserId("r1", "intruder")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().start("intruder", "r1", null)).isInstanceOf(ResumeNotFoundException.class);
		verifyNoInteractions(agentClient);
	}

	@Test
	void getReturnsTheRunRecordWhenTheRunIsOnTheUsersResume() {
		Map<String, Object> run = Map.of("run_id", "run-1", "resume_id", "r1", "status", "completed");
		when(agentClient.getRun("run-1")).thenReturn(run);
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(savedResume()));

		assertThat(service().get("u1", "run-1")).isEqualTo(run);
	}

	@Test
	void anotherUsersRunOrOneWithNoResumeLooksLikeItDoesNotExist() {
		when(agentClient.getRun("run-1")).thenReturn(Map.of("run_id", "run-1", "resume_id", "r1"));
		when(agentClient.getRun("orphan")).thenReturn(Map.of("run_id", "orphan"));
		when(repository.findByIdAndUserId("r1", "intruder")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().get("intruder", "run-1")).isInstanceOf(RunNotFoundException.class);
		assertThatThrownBy(() -> service().get("u1", "orphan")).isInstanceOf(RunNotFoundException.class);
	}

	@Test
	void answerForwardsTheAnswerOnlyForTheOwnersRun() {
		when(agentClient.getRun("run-1")).thenReturn(Map.of("run_id", "run-1", "resume_id", "r1"));
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(savedResume()));
		when(agentClient.answerRun(any(), any())).thenReturn(new RunStarted("run-1", "running"));

		service().answer("u1", "run-1", "Two");

		ArgumentCaptor<AnswerRequest> sent = ArgumentCaptor.forClass(AnswerRequest.class);
		verify(agentClient).answerRun(eq("run-1"), sent.capture());
		assertThat(sent.getValue().getAnswer()).isEqualTo("Two");
	}

	@Test
	void answeringSomeoneElsesRunIsRefusedAndNeverReachesTheAgent() {
		when(agentClient.getRun("run-1")).thenReturn(Map.of("run_id", "run-1", "resume_id", "r1"));
		when(repository.findByIdAndUserId("r1", "intruder")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().answer("intruder", "run-1", "x")).isInstanceOf(RunNotFoundException.class);
		verify(agentClient, never()).answerRun(any(), any());
	}

	@Test
	void aBlankAnswerIsRejectedWithoutCallingTheAgent() {
		assertThatThrownBy(() -> service().answer("u1", "run-1", " ")).isInstanceOf(InvalidRequestException.class);
		verifyNoInteractions(agentClient);
	}
}
