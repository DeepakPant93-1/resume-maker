package com.learning.resumemaker.security;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** The signed-in user as the UI sees them. Never includes the password hash. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserProfile {

	private String id;
	private String email;
	private String name;
}
