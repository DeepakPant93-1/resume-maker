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
import org.springframework.security.oauth2.server.resource.web.authentication.BearerTokenAuthenticationFilter;
import org.springframework.security.web.SecurityFilterChain;

import com.nimbusds.jose.jwk.source.ImmutableSecret;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Global security: every call needs a valid login token (JWT, signed with HS256) except the public paths below.
 * The API is stateless: no session, the token is checked on every request.
 */
@Slf4j
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
@EnableConfigurationProperties(JwtProperties.class)
public class SecurityConfig {

	private static final String[] PUBLIC_PATHS = { "/api/auth/register", "/api/auth/login", "/error",
			"/actuator/health", "/actuator/health/**", "/swagger-ui.html", "/swagger-ui/**", "/v3/api-docs/**" };

	public static final String ISSUER = "resume-maker";
	private static final int MIN_SECRET_BYTES = 32; // HS256 needs a 256-bit key

	private final RestAuthenticationEntryPoint entryPoint;

	/** The one filter chain: public paths are whitelisted, everything else needs a valid bearer token. */
	@Bean
	public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
		log.info("Security: every call needs a login token except the whitelisted public paths");
		return http
				.csrf(AbstractHttpConfigurer::disable) // stateless API with bearer tokens, no cookies to forge
				.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
				.authorizeHttpRequests(requests -> requests
						.requestMatchers(PUBLIC_PATHS).permitAll()
						.anyRequest().authenticated())
				.exceptionHandling(handling -> handling.authenticationEntryPoint(entryPoint))
				.oauth2ResourceServer(resource -> resource.jwt(Customizer.withDefaults())
						.authenticationEntryPoint(entryPoint))
				.addFilterAfter(new JwtFilter(), BearerTokenAuthenticationFilter.class)
				.build();
	}

	/** The HS256 signing key, built from the configured secret. */
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

	/** Signs the login tokens. */
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

	/** BCrypt for password hashes. */
	@Bean
	public PasswordEncoder passwordEncoder() {
		return new BCryptPasswordEncoder();
	}
}
