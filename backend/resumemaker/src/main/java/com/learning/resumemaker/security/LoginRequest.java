package com.learning.resumemaker.security;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Builder;

/** Login form from the UI. */
@Builder
@Schema(description = "Login form")
public record LoginRequest(
		@NotBlank(message = "Email is required") String email,
		@NotBlank(message = "Password is required") String password) {
}
