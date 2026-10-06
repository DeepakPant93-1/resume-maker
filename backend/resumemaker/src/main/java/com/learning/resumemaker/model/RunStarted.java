package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** The agent service's acknowledgement that a run started or continued. Poll the run for its progress. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RunStarted {

	private String runId;
	private String status;
}
