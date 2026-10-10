package com.learning.resumemaker.web;

import java.util.UUID;
import java.util.regex.Pattern;

import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Per-request boilerplate in one place: resolves the request-id (header or a new UUID), puts it in MDC, echoes it as
 * the response-id header and reports how long the API took.
 */
@Component
public class RequestContextInterceptor implements HandlerInterceptor {

	public static final String REQUEST_ID_HEADER = "request-id";
	public static final String RESPONSE_ID_HEADER = "response-id";
	public static final String RESPONSE_TIME_HEADER = "X-Response-Time-Ms";
	public static final String REQUEST_ID_KEY = "requestId";

	private static final String START_ATTRIBUTE = RequestContextInterceptor.class.getName() + ".start";
	/** A client-supplied id ends up in logs and headers, so only a short, plain one is accepted. */
	private static final Pattern SAFE_ID = Pattern.compile("[A-Za-z0-9._-]{1,100}");

	/** Starts the timer, stores the request-id in MDC and sets the response-id header. */
	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
		request.setAttribute(START_ATTRIBUTE, System.nanoTime());
		String requestId = resolveRequestId(request.getHeader(REQUEST_ID_HEADER));
		MDC.put(REQUEST_ID_KEY, requestId);
		response.setHeader(RESPONSE_ID_HEADER, requestId);
		return true;
	}

	/** Sets the time-taken header once the handler has run (before the response is committed). */
	@Override
	public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler,
			org.springframework.web.servlet.ModelAndView modelAndView) {
		Object start = request.getAttribute(START_ATTRIBUTE);
		if (start instanceof Long startNanos && !response.isCommitted()) {
			response.setHeader(RESPONSE_TIME_HEADER, String.valueOf((System.nanoTime() - startNanos) / 1_000_000));
		}
	}

	/** Clears the request-id from MDC when the request completes. */
	@Override
	public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler,
			Exception ex) {
		MDC.remove(REQUEST_ID_KEY);
	}

	private static String resolveRequestId(String header) {
		return header != null && SAFE_ID.matcher(header).matches() ? header : UUID.randomUUID().toString();
	}
}
