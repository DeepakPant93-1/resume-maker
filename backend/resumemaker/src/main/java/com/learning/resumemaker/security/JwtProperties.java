package com.learning.resumemaker.security;

import java.time.Duration;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** Settings for the login tokens: the HS256 signing secret and how long a token stays valid. */
@ConfigurationProperties(prefix = "app.jwt")
public record JwtProperties(String secret, Duration expiry) {
}
