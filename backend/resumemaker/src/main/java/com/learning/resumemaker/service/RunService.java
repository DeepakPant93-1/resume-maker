package com.learning.resumemaker.service;

import java.util.Map;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.exception.InvalidRequestException;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.exception.RunNotFoundException;
import com.learning.resumemaker.mapper.ResumeMapper;
import com.learning.resumemaker.model.AgentRunRequest;
import com.learning.resumemaker.model.AnswerRequest;
import com.learning.resumemaker.model.RunStarted;
import com.learning.resumemaker.repository.ResumeRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Starts AI runs on saved resumes and relays progress and answers between the UI and the agent service. */
@Slf4j
@Service
@RequiredArgsConstructor
public class RunService {

	private final ResumeRepository repository;
	private final ResumeMapper mapper;
	private final AgentClient agentClient;

	/** Sends the saved resume (and the job description, if any) to the agent service. */
	public RunStarted start(String userId, String resumeId, String jobDescription) {
		var resume = repository.findByIdAndUserId(resumeId, userId).orElseThrow(() -> {
			log.warn("Run rejected: resume {} not found", resumeId);
			return new ResumeNotFoundException(resumeId);
		});
		String job = jobDescription == null || jobDescription.isBlank() ? null : jobDescription;
		log.info("Starting agent run for resume {} (job description: {})", resumeId, job == null ? "none" : job.length() + " chars");
		RunStarted started = agentClient.startRun(
				AgentRunRequest.builder().resume(mapper.toResponse(resume)).jobDescription(job).build());
		log.info("Agent run {} started for resume {}", started.getRunId(), resumeId);
		return started;
	}

	/** The run record (status, question, output, state) exactly as the agent service reports it. */
	public Map<String, Object> get(String userId, String runId) {
		return ownRun(userId, runId);
	}

	/** Gives a paused run the user's answer so it can continue. */
	public RunStarted answer(String userId, String runId, String answer) {
		if (answer == null || answer.isBlank()) {
			throw new InvalidRequestException("An answer is required");
		}
		ownRun(userId, runId);
		log.info("Answering agent run {}", runId);
		return agentClient.answerRun(runId, AnswerRequest.builder().answer(answer).build());
	}

	/**
	 * The run record, but only if the run belongs to this user (it was started on one of their resumes). Someone
	 * else's run, or one with no resume attached, looks exactly like a run that does not exist.
	 */
	private Map<String, Object> ownRun(String userId, String runId) {
		Map<String, Object> run = agentClient.getRun(runId);
		Object resumeId = run.get("resume_id");
		if (!(resumeId instanceof String id) || repository.findByIdAndUserId(id, userId).isEmpty()) {
			log.warn("User {} asked for run {}, which is not theirs or does not exist", userId, runId);
			throw new RunNotFoundException(runId);
		}
		return run;
	}
}
