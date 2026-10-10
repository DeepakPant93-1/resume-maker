package com.learning.resumemaker.web;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/** The request-id / response-id / timing boilerplate. */
class RequestContextInterceptorTest {

	private final RequestContextInterceptor interceptor = new RequestContextInterceptor();
	private final MockHttpServletRequest request = new MockHttpServletRequest();
	private final MockHttpServletResponse response = new MockHttpServletResponse();

	@AfterEach
	void clean() {
		MDC.clear();
	}

	@Test
	void theRequestIdIsEchoedAsTheResponseIdAndPutInMdc() {
		request.addHeader("request-id", "abc-123");

		interceptor.preHandle(request, response, new Object());

		assertThat(response.getHeader("response-id")).isEqualTo("abc-123");
		assertThat(MDC.get("requestId")).isEqualTo("abc-123");
	}

	@Test
	void aMissingOrUnsafeRequestIdIsReplacedByAUuid() {
		interceptor.preHandle(request, response, new Object());
		String generated = response.getHeader("response-id");
		assertThat(generated).hasSize(36);

		MockHttpServletResponse second = new MockHttpServletResponse();
		MockHttpServletRequest unsafe = new MockHttpServletRequest();
		unsafe.addHeader("request-id", "bad id with spaces");
		interceptor.preHandle(unsafe, second, new Object());
		assertThat(second.getHeader("response-id")).hasSize(36);
	}

	@Test
	void theTimeTakenIsReturnedAndMdcIsClearedAtTheEnd() {
		interceptor.preHandle(request, response, new Object());

		interceptor.postHandle(request, response, new Object(), null);
		interceptor.afterCompletion(request, response, new Object(), null);

		assertThat(response.getHeader("X-Response-Time-Ms")).matches("\\d+");
		assertThat(MDC.get("requestId")).isNull();
	}
}
