package com.learning.resumemaker.security;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Login form from the UI. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequest {

	private String email;
	private String password;
}
