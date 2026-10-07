package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Body of POST /api/runs on the agent service: the resume plus an optional job description. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentRunRequest {

	private ResumeResponse resume;
	private String jobDescription;
}
