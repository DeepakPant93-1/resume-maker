package com.learning.resumemaker.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Profile {

	private String fullName;
	private String jobTitle;
	private String email;
	private String phone;
	private String location;
	private String linkedin;
	private String summary;
}
