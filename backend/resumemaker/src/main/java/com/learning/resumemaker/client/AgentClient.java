package com.learning.resumemaker.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;

/** Client for the Python agent service (backend/agents). */
@FeignClient(name = "agent-service", url = "${agent.service.url}")
public interface AgentClient {

	/** Instant, model-free ATS score of a resume, optionally against a job description. */
	@PostMapping("/api/ats")
	AtsReport atsScore(@RequestBody AtsRequest request);

	/** One model call: a new professional summary for the resume, or an improved version of the one given. */
	@PostMapping("/api/summary")
	SummaryResponse writeSummary(@RequestBody SummaryRequest request);
}
