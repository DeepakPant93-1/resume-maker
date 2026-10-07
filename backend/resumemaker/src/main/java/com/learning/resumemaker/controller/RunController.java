package com.learning.resumemaker.controller;

import java.util.Map;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.AnswerRequest;
import com.learning.resumemaker.model.RunStarted;
import com.learning.resumemaker.model.StartRunRequest;
import com.learning.resumemaker.service.RunService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** AI runs: start one on a saved resume, poll it, and answer its questions. The work happens in the agent service. */
@Slf4j
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class RunController {

	private final RunService service;

	@PostMapping("/resumes/{id}/runs")
	public RunStarted start(@AuthenticationPrincipal Jwt jwt, @PathVariable String id,
			@RequestBody(required = false) StartRunRequest request) {
		log.info("POST /api/resumes/{}/runs", id);
		return service.start(jwt.getSubject(), id, request == null ? null : request.getJobDescription());
	}

	@GetMapping("/runs/{runId}")
	public Map<String, Object> get(@AuthenticationPrincipal Jwt jwt, @PathVariable String runId) {
		return service.get(jwt.getSubject(), runId);
	}

	@PostMapping("/runs/{runId}/resume")
	public RunStarted answer(@AuthenticationPrincipal Jwt jwt, @PathVariable String runId,
			@RequestBody AnswerRequest request) {
		log.info("POST /api/runs/{}/resume", runId);
		return service.answer(jwt.getSubject(), runId, request.getAnswer());
	}
}
