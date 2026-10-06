package com.learning.resumemaker.model;

import java.time.Instant;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** One row of the user's resume list (the dashboard): enough to show a card, not the whole resume. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeSummary {

	private String id;
	private String title;
	/** ATS score from the last save, or null if it could not be computed (for example the agent service was down). */
	private Integer atsScore;
	private Instant updatedAt;
}
