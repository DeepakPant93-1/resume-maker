package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** What the UI sends to start an AI run on a saved resume. The job description is optional. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StartRunRequest {

	private String jobDescription;
}
