package com.learning.resumemaker.security;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Create-account form from the UI. The name is optional. */
@Builder
@Schema(description = "Create-account form")
public record RegisterRequest(
		@Size(max = 200) String name,
		@NotBlank(message = "Please enter a valid email address")
		@Pattern(regexp = "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", message = "Please enter a valid email address")
		@Size(max = 254) String email,
		@NotBlank(message = "The password must be at least 8 characters")
		@Size(min = 8, message = "The password must be at least 8 characters") String password) {
}
