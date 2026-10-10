package com.learning.resumemaker.security;

import java.io.IOException;

import org.slf4j.MDC;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Runs right after Spring Security has verified the bearer token: copies the token's subject (the user id) into
 * {@link UserContext} and MDC for the rest of the request, and always clears both afterwards.
 */
public class JwtFilter extends OncePerRequestFilter {

	public static final String USER_ID_KEY = "userId";

	/** Publishes the authenticated user id for this request and clears it in a finally block. */
	@Override
	protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
			throws ServletException, IOException {
		try {
			Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
			if (authentication instanceof JwtAuthenticationToken token && token.isAuthenticated()) {
				String userId = token.getToken().getSubject();
				UserContext.setUserId(userId);
				MDC.put(USER_ID_KEY, userId);
			}
			chain.doFilter(request, response);
		} finally {
			UserContext.clear();
			MDC.remove(USER_ID_KEY);
		}
	}
}
