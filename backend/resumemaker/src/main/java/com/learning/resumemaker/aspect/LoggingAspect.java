package com.learning.resumemaker.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.stereotype.Component;

import lombok.extern.slf4j.Slf4j;

/**
 * Logs entry and exit of every controller and service method. Only the method name and duration are logged, never
 * arguments or results, which may hold personal data. Exceptions are not logged here: the GlobalExceptionHandler does.
 */
@Slf4j
@Aspect
@Component
public class LoggingAspect {

	/** Matches every method of the application's REST controllers. */
	@Pointcut("within(@org.springframework.web.bind.annotation.RestController *)")
	void controllers() {
	}

	/** Matches every method of the application's services. */
	@Pointcut("within(@org.springframework.stereotype.Service *) && within(com.learning.resumemaker..*)")
	void services() {
	}

	/** Logs entry and exit around a controller or service method. */
	@Around("controllers() || services()")
	public Object logEntryAndExit(ProceedingJoinPoint joinPoint) throws Throwable {
		String method = joinPoint.getSignature().getDeclaringType().getSimpleName() + "."
				+ joinPoint.getSignature().getName();
		long start = System.nanoTime();
		log.debug("-> {}", method);
		try {
			Object result = joinPoint.proceed();
			log.debug("<- {} ({} ms)", method, (System.nanoTime() - start) / 1_000_000);
			return result;
		} catch (Throwable ex) {
			log.debug("<- {} failed ({} ms)", method, (System.nanoTime() - start) / 1_000_000);
			throw ex;
		}
	}
}
