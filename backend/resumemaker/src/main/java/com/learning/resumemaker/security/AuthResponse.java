package com.learning.resumemaker.security;

import java.time.Instant;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Result of a successful login or registration: the token to send on every later call, and who it belongs to. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

	private String token;
	private Instant expiresAt;
	private UserProfile user;
}
