package com.learning.resumemaker.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.learning.resumemaker.web.RequestContextInterceptor;

import lombok.RequiredArgsConstructor;

/** Registers the request-id / timing interceptor for the API. */
@Configuration
@RequiredArgsConstructor
public class WebConfig implements WebMvcConfigurer {

	private final RequestContextInterceptor requestContextInterceptor;

	/** Applies the interceptor to every /api call. */
	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(requestContextInterceptor).addPathPatterns("/api/**");
	}
}
