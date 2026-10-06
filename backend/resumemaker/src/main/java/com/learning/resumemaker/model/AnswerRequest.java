package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** The user's answer to the question a paused run is waiting on. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnswerRequest {

	private String answer;
}
