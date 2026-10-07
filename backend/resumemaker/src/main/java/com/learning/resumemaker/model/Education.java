package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Education {

	private String degree;
	private String university;
	private String startYear;
	private String endYear;
	private String grade;
	private String location;
}
