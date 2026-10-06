package com.learning.resumemaker.config;

import java.time.Clock;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ClockConfig {

	/** One clock for the whole app, so tests can substitute a fixed one. */
	@Bean
	public Clock clock() {
		return Clock.systemUTC();
	}
}
