package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * The resume as the editor has it, plus the summary typed so far (blank means write a new one).
 * It is the body of both the UI's call and the call on to the agent service.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SummaryRequest {

	private ResumeRequest resume;
	private String summary;
}
