package com.learning.resumemaker.security;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Create-account form from the UI. The name is optional. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

	private String name;
	private String email;
	private String password;
}
