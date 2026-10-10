package com.learning.resumemaker.security;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import javax.crypto.SecretKey;

import org.junit.jupiter.api.Test;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtException;

import com.learning.resumemaker.document.UserDocument;

/** The tokens the API hands out, checked with the same decoder that guards every request. */
class JwtServiceTest {

	private static final String SECRET = "test-secret-that-is-long-enough-for-hs256-0123456789";
	private final SecurityConfig config = new SecurityConfig(null);

	private JwtProperties properties(String secret) {
		return new JwtProperties(secret, Duration.ofHours(8));
	}

	private JwtService service(String secret, Clock clock) {
		SecretKey key = config.jwtSecretKey(properties(secret));
		return new JwtService(config.jwtEncoder(key), properties(secret), clock);
	}

	private JwtDecoder decoder(String secret) {
		return config.jwtDecoder(config.jwtSecretKey(properties(secret)));
	}

	private UserDocument user() {
		return UserDocument.builder().id("u1").email("suraj@example.com").name("Suraj").build();
	}

	@Test
	void aFreshTokenDecodesToTheUserAndExpiresAfterTheConfiguredTime() {
		Instant now = Instant.now();
		JwtService.IssuedToken token = service(SECRET, Clock.fixed(now, ZoneOffset.UTC)).issue(user());

		Jwt jwt = decoder(SECRET).decode(token.value());

		assertThat(jwt.getSubject()).isEqualTo("u1");
		assertThat(jwt.getClaimAsString("email")).isEqualTo("suraj@example.com");
		assertThat(jwt.getClaimAsString("name")).isEqualTo("Suraj");
		assertThat(jwt.getClaimAsString("iss")).isEqualTo(SecurityConfig.ISSUER);
		assertThat(Duration.between(now, token.expiresAt())).isEqualTo(Duration.ofHours(8));
	}

	@Test
	void anExpiredTokenIsRejected() {
		Instant longAgo = Instant.now().minus(Duration.ofDays(2));
		String token = service(SECRET, Clock.fixed(longAgo, ZoneOffset.UTC)).issue(user()).value();

		assertThatThrownBy(() -> decoder(SECRET).decode(token)).isInstanceOf(JwtException.class)
				.hasMessageContaining("expired");
	}

	@Test
	void aTokenSignedWithAnotherKeyIsRejected() {
		String forged = service("another-secret-that-is-also-long-enough-9876543210", Clock.systemUTC()).issue(user()).value();

		assertThatThrownBy(() -> decoder(SECRET).decode(forged)).isInstanceOf(JwtException.class);
	}

	@Test
	void aTokenWhoseContentWasEditedIsRejected() {
		String token = service(SECRET, Clock.systemUTC()).issue(user()).value();
		String[] parts = token.split("\\.");
		// swap in a payload that claims to be another user, keeping the original signature
		String payload = java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(
				("{\"iss\":\"resume-maker\",\"sub\":\"someone-else\",\"exp\":" + (Instant.now().getEpochSecond() + 3600) + "}")
						.getBytes(java.nio.charset.StandardCharsets.UTF_8));
		String tampered = parts[0] + "." + payload + "." + parts[2];

		assertThatThrownBy(() -> decoder(SECRET).decode(tampered)).isInstanceOf(JwtException.class);
	}

	@Test
	void aSecretShorterThan32BytesIsRefusedAtStartup() {
		assertThatThrownBy(() -> config.jwtSecretKey(properties("too-short")))
				.isInstanceOf(IllegalStateException.class).hasMessageContaining("at least 32 bytes");
	}
}
