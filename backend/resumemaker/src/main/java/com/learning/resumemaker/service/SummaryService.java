package com.learning.resumemaker.service;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.exception.InvalidRequestException;
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

	/** Works on the resume exactly as sent, so unsaved edits count. Nothing is stored. */
	public SummaryResponse write(SummaryRequest request) {
		if (request == null || request.getResume() == null) {
			log.warn("Summary rejected: no resume in the request");
			throw new InvalidRequestException("A resume is required");
		}
		String existing = request.getSummary();
		existing = existing == null || existing.isBlank() ? null : existing;
		log.info("Writing summary ({})", existing == null ? "new" : "improving " + existing.length() + " chars");
		return agentClient.writeSummary(
				SummaryRequest.builder().resume(request.getResume()).summary(existing).build());
	}
}
