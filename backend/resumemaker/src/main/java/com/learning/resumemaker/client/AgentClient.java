package com.learning.resumemaker.client;

import java.util.Map;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.learning.resumemaker.model.AgentRunRequest;
import com.learning.resumemaker.model.AnswerRequest;
import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.model.RunStarted;
import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;

/** Client for the Python agent service (backend/agents). */
@FeignClient(name = "agent-service", url = "${agent.service.url}")
public interface AgentClient {

	@PostMapping("/api/runs")
	RunStarted startRun(@RequestBody AgentRunRequest request);

	/** The run record as the agent service returns it (status, question, output, state...), passed through as-is. */
	@GetMapping("/api/runs/{runId}")
	Map<String, Object> getRun(@PathVariable("runId") String runId);

	@PostMapping("/api/runs/{runId}/resume")
	RunStarted answerRun(@PathVariable("runId") String runId, @RequestBody AnswerRequest request);

	/** Instant, model-free ATS score of a resume, optionally against a job description. */
	@PostMapping("/api/ats")
	AtsReport atsScore(@RequestBody AtsRequest request);

	/** One model call: a new professional summary for the resume, or an improved version of the one given. */
	@PostMapping("/api/summary")
	SummaryResponse writeSummary(@RequestBody SummaryRequest request);
}
