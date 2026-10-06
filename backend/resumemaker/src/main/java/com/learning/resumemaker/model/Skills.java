package com.learning.resumemaker.model;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Skills {

	private List<String> languages;
	private List<String> frameworks;
	private List<String> tools;
}
