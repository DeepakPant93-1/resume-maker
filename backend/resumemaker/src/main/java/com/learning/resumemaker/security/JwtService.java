package com.learning.resumemaker.security;

import java.time.Clock;
import java.time.Instant;

import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.UserDocument;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Creates the signed login tokens. Checking them on incoming calls is done by Spring Security's JwtDecoder. */
@Slf4j
@Service
@RequiredArgsConstructor
public class JwtService {

	private final JwtEncoder encoder;
	private final JwtProperties properties;
	private final Clock clock;

	/** A signed token and the moment it stops being valid. */
	public record IssuedToken(String value, Instant expiresAt) {
	}

	/**
	 * Signs a token whose subject is the user's id, so every later call can be tied to its owner.
	 */
	public IssuedToken issue(UserDocument user) {
		Instant now = clock.instant();
		Instant expiresAt = now.plus(properties.expiry());
		JwtClaimsSet claims = JwtClaimsSet.builder()
				.issuer(SecurityConfig.ISSUER)
				.subject(user.getId())
				.issuedAt(now)
				.expiresAt(expiresAt)
				.claim("email", user.getEmail())
				.claim("name", user.getName())
				.build();
		String token = encoder.encode(JwtEncoderParameters.from(JwsHeader.with(MacAlgorithm.HS256).build(), claims))
				.getTokenValue();
		log.info("Issued a login token for user {}, valid until {}", user.getId(), expiresAt);
		return new IssuedToken(token, expiresAt);
	}
}
