package com.learning.resumemaker.service;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.client.AgentClient;
import com.learning.resumemaker.exception.InvalidRequestException;
import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.model.ResumeRequest;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Scores a resume for ATS readability and, if a job description is given, keyword match. */
@Slf4j
@Service
@RequiredArgsConstructor
public class AtsService {

	private final AgentClient agentClient;

	/** Scores the resume exactly as sent, so unsaved edits can be checked. Nothing is stored. */
	public AtsReport check(AtsRequest request) {
		if (request == null || request.getResume() == null) {
			log.warn("ATS check rejected: no resume in the request");
			throw new InvalidRequestException("A resume is required");
		}
		String job = request.getJobDescription();
		job = job == null || job.isBlank() ? null : job;
		log.info("ATS check (job description: {})", job == null ? "none" : job.length() + " chars");
		AtsReport report = agentClient.atsScore(
				AtsRequest.builder().resume(request.getResume()).jobDescription(job).build());
		log.info("ATS check done: {}/100", report.getScore());
		return report;
	}

	/**
	 * Score to store with a saved resume. Best effort: if the agent service is down the save must still work,
	 * so a failure is logged and null is returned.
	 */
	public Integer scoreOrNull(ResumeRequest resume) {
		try {
			return check(new AtsRequest(resume, null)).getScore();
		} catch (RuntimeException e) {
			log.warn("Could not compute the ATS score to store with the resume: {}", e.getMessage());
			return null;
		}
	}
}
