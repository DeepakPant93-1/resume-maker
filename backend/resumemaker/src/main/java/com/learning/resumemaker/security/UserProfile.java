package com.learning.resumemaker.security;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

/** The signed-in user as the UI sees them. Never includes the password hash. */
@Builder
@Schema(description = "The signed-in user")
public record UserProfile(String id, String email, String name) {
}
