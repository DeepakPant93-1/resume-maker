package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * A resume to score for ATS, plus an optional job description (with it the score includes keyword match).
 * It is the body of both the UI's call and the call on to the agent service.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AtsRequest {

	private ResumeRequest resume;
	private String jobDescription;
}
