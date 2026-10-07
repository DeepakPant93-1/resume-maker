package com.learning.resumemaker.model;

import java.util.List;
import java.util.Map;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** ATS score out of 100 with its parts and suggestions, as computed by the agent service. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AtsReport {

	private Integer score;
	private boolean againstJob;
	private Map<String, AtsComponent> components;
	private List<String> suggestions;
}
