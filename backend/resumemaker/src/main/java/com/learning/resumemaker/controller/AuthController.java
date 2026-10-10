package com.learning.resumemaker.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.ErrorResponse;
import com.learning.resumemaker.security.AuthResponse;
import com.learning.resumemaker.security.AuthService;
import com.learning.resumemaker.security.LoginRequest;
import com.learning.resumemaker.security.RegisterRequest;
import com.learning.resumemaker.security.UserProfile;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirements;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

/** Register and log in (public), and ask who the token belongs to (needs a token). */
@Tag(name = "Auth", description = "Register, log in and identify the signed-in user")
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

	private final AuthService service;

	/** Creates an account and signs it in. */
	@Operation(summary = "Create an account")
	@SecurityRequirements
	@ApiResponse(responseCode = "201", description = "Account created")
	@ApiResponse(responseCode = "400", description = "Invalid form", content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
	@ApiResponse(responseCode = "409", description = "Email already registered", content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
	@PostMapping("/register")
	public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
		return ResponseEntity.status(HttpStatus.CREATED).body(service.register(request));
	}

	/** Checks the credentials and returns a token. */
	@Operation(summary = "Log in")
	@SecurityRequirements
	@ApiResponse(responseCode = "200", description = "Logged in")
	@ApiResponse(responseCode = "401", description = "Invalid email or password", content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
	@PostMapping("/login")
	public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
		return ResponseEntity.ok(service.login(request));
	}

	/** The user the token belongs to. */
	@Operation(summary = "Get the signed-in user")
	@ApiResponse(responseCode = "200", description = "The user")
	@ApiResponse(responseCode = "401", description = "Missing, invalid or expired token", content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
	@GetMapping("/me")
	public ResponseEntity<UserProfile> getCurrentUser() {
		return ResponseEntity.ok(service.getProfile());
	}
}
