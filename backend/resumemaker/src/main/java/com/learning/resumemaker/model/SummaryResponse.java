package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** The professional summary written by the agent service. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SummaryResponse {

	private String summary;
}
