package com.learning.resumemaker.security;

import java.nio.charset.StandardCharsets;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtTimestampValidator;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtEncoder;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.SecurityFilterChain;

import com.nimbusds.jose.jwk.source.ImmutableSecret;

import lombok.extern.slf4j.Slf4j;

/**
 * Every /api call needs a valid login token (JWT, signed with HS256) except register and login.
 * The API is stateless: no session, the token is checked on every request.
 */
@Slf4j
@Configuration
@EnableWebSecurity
@EnableConfigurationProperties(JwtProperties.class)
public class SecurityConfig {

	public static final String ISSUER = "resume-maker";
	private static final int MIN_SECRET_BYTES = 32; // HS256 needs a 256-bit key

	@Bean
	public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
		AuthenticationEntryPoint unauthorized = (request, response, exception) -> {
			// The reason says whether the token was missing, expired, edited or signed with another key. The token is never logged.
			log.warn("Rejected {} {}: {}", request.getMethod(), request.getRequestURI(), exception.getMessage());
			response.setStatus(401);
			response.setContentType("application/json");
			response.getWriter().write("{\"message\":\"Please log in again: the login token is missing, invalid or expired\"}");
		};
		log.info("Security: every /api call needs a login token except register and login");
		return http
				.csrf(AbstractHttpConfigurer::disable) // stateless API with bearer tokens, no cookies to forge
				.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
				.authorizeHttpRequests(requests -> requests
						.requestMatchers("/api/auth/register", "/api/auth/login", "/error").permitAll()
						.anyRequest().authenticated())
				.exceptionHandling(handling -> handling.authenticationEntryPoint(unauthorized))
				.oauth2ResourceServer(resource -> resource.jwt(Customizer.withDefaults())
						.authenticationEntryPoint(unauthorized))
				.build();
	}

	@Bean
	public SecretKey jwtSecretKey(JwtProperties properties) {
		byte[] secret = properties.secret().getBytes(StandardCharsets.UTF_8);
		if (secret.length < MIN_SECRET_BYTES) {
			throw new IllegalStateException("app.jwt.secret must be at least " + MIN_SECRET_BYTES + " bytes long");
		}
		if (properties.secret().startsWith("dev-only")) {
			log.warn("Login tokens are signed with the built-in development secret. Set JWT_SECRET before deploying.");
		}
		return new SecretKeySpec(secret, "HmacSHA256");
	}

	@Bean
	public JwtEncoder jwtEncoder(SecretKey jwtSecretKey) {
		return new NimbusJwtEncoder(new ImmutableSecret<>(jwtSecretKey));
	}

	/** Verifies the signature, the expiry and the issuer of every incoming token. */
	@Bean
	public JwtDecoder jwtDecoder(SecretKey jwtSecretKey) {
		NimbusJwtDecoder decoder = NimbusJwtDecoder.withSecretKey(jwtSecretKey).macAlgorithm(MacAlgorithm.HS256).build();
		OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(new JwtTimestampValidator(),
				JwtValidators.createDefaultWithIssuer(ISSUER));
		decoder.setJwtValidator(validator);
		log.info("Login tokens are verified for signature (HS256), expiry and issuer '{}'", ISSUER);
		return decoder;
	}

	@Bean
	public PasswordEncoder passwordEncoder() {
		return new BCryptPasswordEncoder();
	}
}
