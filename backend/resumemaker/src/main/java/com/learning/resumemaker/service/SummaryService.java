package com.learning.resumemaker.service;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Writes (or improves) the professional summary of the resume being edited. The writing happens in the agent service. */
@Slf4j
@Service
@RequiredArgsConstructor
public class SummaryService {

	private final AgentClient agentClient;

	/**
	 * Works on the resume exactly as sent, so unsaved edits count. Nothing is stored.
	 *
	 * @param request the resume and the summary typed so far (blank means write a new one)
	 * @return the written summary
	 */
	public SummaryResponse writeSummary(SummaryRequest request) {
		String existing = request.summary() == null || request.summary().isBlank() ? null : request.summary();
		log.info("Writing summary ({})", existing == null ? "new" : "improving " + existing.length() + " chars");
		return agentClient.writeSummary(SummaryRequest.builder().resume(request.resume()).summary(existing).build());
	}
}
