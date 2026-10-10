package com.learning.resumemaker.security;

import java.time.Instant;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** Result of a successful login or registration: the token to send on every later call, and who it belongs to. */
@Builder
@Schema(description = "Token and user after a successful login or registration")
public record AuthResponse(String token, Instant expiresAt, UserProfile user) {

	/** Hides the token, so a logged response never leaks it. */
	@Override
	public String toString() {
		return "AuthResponse[expiresAt=" + expiresAt + ", user=" + user + "]";
	}
}
