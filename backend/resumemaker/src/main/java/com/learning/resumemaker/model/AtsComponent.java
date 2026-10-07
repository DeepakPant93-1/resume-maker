package com.learning.resumemaker.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** One part of the ATS score. Which detail fields are filled depends on the part (keywords, completeness, impact, readability). */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AtsComponent {

	private Double points;
	private Integer max;
	private List<String> matched;
	private List<String> missing;
	private Integer bullets;
	private Integer withNumbers;
	private Integer longBullets;
	private Integer summaryWords;
}
