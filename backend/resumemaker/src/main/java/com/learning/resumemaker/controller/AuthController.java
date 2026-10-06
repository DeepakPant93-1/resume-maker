package com.learning.resumemaker.controller;

import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.security.AuthResponse;
import com.learning.resumemaker.security.AuthService;
import com.learning.resumemaker.security.LoginRequest;
import com.learning.resumemaker.security.RegisterRequest;
import com.learning.resumemaker.security.UserProfile;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Register and log in (public), and ask who the token belongs to (needs a token). */
@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

	private final AuthService service;

	@PostMapping("/register")
	@ResponseStatus(HttpStatus.CREATED)
	public AuthResponse register(@RequestBody RegisterRequest request) {
		log.info("POST /api/auth/register");
		return service.register(request);
	}

	@PostMapping("/login")
	public AuthResponse login(@RequestBody LoginRequest request) {
		log.info("POST /api/auth/login");
		return service.login(request);
	}

	@GetMapping("/me")
	public UserProfile me(@AuthenticationPrincipal Jwt jwt) {
		log.info("GET /api/auth/me - user {}", jwt.getSubject());
		return service.profile(jwt.getSubject());
	}
}
