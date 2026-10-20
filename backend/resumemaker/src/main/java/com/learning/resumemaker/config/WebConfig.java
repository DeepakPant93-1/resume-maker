package com.learning.resumemaker.config;

import java.util.Locale;

import org.springframework.context.annotation.Configuration;
import org.springframework.format.FormatterRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.learning.resumemaker.model.ExportFormat;
import com.learning.resumemaker.web.RequestContextInterceptor;

import lombok.RequiredArgsConstructor;

/** Registers the request-id / timing interceptor and the request-parameter converters for the API. */
@Configuration
@RequiredArgsConstructor
public class WebConfig implements WebMvcConfigurer {

	private final RequestContextInterceptor requestContextInterceptor;

	/** Applies the interceptor to every /api call. */
	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(requestContextInterceptor).addPathPatterns("/api/**");
	}

	/** Reads ?format= in any case ("pdf", "PDF"); an unknown value is a 400 through the type-mismatch handler. */
	@Override
	public void addFormatters(FormatterRegistry registry) {
		registry.addConverter(String.class, ExportFormat.class,
				value -> ExportFormat.valueOf(value.trim().toUpperCase(Locale.ROOT)));
	}
}
