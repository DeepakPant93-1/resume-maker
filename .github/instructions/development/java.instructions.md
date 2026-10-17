---
name: Java Development
description: Java 25 / Spring Boot coding standards for AI agents to follow when writing or modifying Java code in this repository.
applyTo: "**/*.java"
---

# Java Development Instructions

## Language & Style
- Use Java 25 syntax and features (records, sealed types, pattern matching, switch expressions, text blocks, `var` where it aids readability).
- Use Lombok where it removes boilerplate, e.g. `@Slf4j`, `@RequiredArgsConstructor`, `@Getter`, `@Builder`.
- Prefer constructor injection via `@RequiredArgsConstructor`; avoid field `@Autowired`.
- Write class-based, OOP-style code (route/controller classes, base classes, service classes).

## Naming
- Method names must be in camelCase; prefer an action/verb (e.g. `getResume`, `generateSummary`, `validateToken`).
- Class names must start with a capital letter (PascalCase); prefer a noun (e.g. `ResumeService`, `UserContext`, `JwtFilter`).

## Javadoc
- Add a brief Javadoc on every class and on every method.
- Keep it short and crisp: a one-line summary of purpose; add `@param` / `@return` / `@throws` only when not obvious.

## Configuration
- Use only `application.yaml` for properties. Do not add `application.properties`.

## REST APIs
- Create APIs with `@RestController`.
- Always return `ResponseEntity` from controller methods.
- Expose endpoints with Swagger/springdoc and follow the OpenAPI standard (annotate with `@Operation`, `@ApiResponse`, `@Tag`, and document request/response schemas).
- Controllers contain no validation logic and no business logic; they delegate to services.

### Request Validation
- Always validate incoming payloads with Spring `@Valid` / `@Validated` and Jakarta Validation annotations (`@NotNull`, `@NotBlank`, `@Size`, `@Pattern`, type checks, etc.) on request DTOs.
- Never perform manual validation in the controller layer.

### Request / Response Headers
- Accept a `request-id` request header. It is optional; if absent, generate a UUID.
- Always return the same value in the response header as `response-id`.
- Always return the time taken by the API in a response header (e.g. `X-Response-Time-Ms`).
- Implement this boilerplate once in a Spring `HandlerInterceptor` (registered through `WebMvcConfigurer`) that: resolves/generates the request-id, starts the timer, and sets the `response-id` and time-taken headers. Do not repeat this logic in controllers.

## Exception Handling
- Create a super custom exception class (e.g. `BaseException extends RuntimeException`) that is the parent of all custom exceptions.
- Always create custom exceptions for domain/application errors, extending that base class.
- Always create a `GlobalExceptionHandler` (`@RestControllerAdvice`) that handles the custom exceptions, validation errors (`MethodArgumentNotValidException`, etc.) and a generic fallback, returning a consistent error body via `ResponseEntity`.

## Logging
- Use `@Slf4j`.
- Use a common logging Aspect (Spring AOP) to log method entry and exit for controller and service classes. Do not write entry/exit logs manually in every API or method.
- In service classes, add logs only where they add value (e.g. the file name being processed, key business steps).
- Never log sensitive user data: passwords, tokens, names, phone numbers, emails, or other PII.
- Always include the request-id and the user-id (if present) in logs: store them in MDC (keys `requestId`, `userId`) and reference them in the log pattern in `application.yaml`. Set `requestId` in the interceptor, `userId` in the JWT filter, and clear MDC when the request completes.

### Exception Logging
- Do not print unnecessary stack traces. Never log a stack trace for client errors such as 400, 401, 403 or 404.
- Print the stack trace only for server errors (5xx), e.g. `log.error("message", ex)` in the `GlobalExceptionHandler` fallback.
- For all other exceptions, log only the relevant error message (e.g. `log.warn("Request failed: {}", ex.getMessage())`), without passing the exception object.
- Log each exception once, in the `GlobalExceptionHandler`; do not log-and-rethrow in services or controllers.

## Third-Party API Calls
- Always use Spring Cloud OpenFeign (`@FeignClient`) to call third-party APIs. Do not use `RestTemplate`, `WebClient`, or raw HTTP clients.

## Security
- Create a single global security config (`SecurityFilterChain`) that secures all endpoints; explicitly whitelist public paths (e.g. Swagger UI, health).
- Secure endpoints with JWT. Read the token from the request header (`Authorization: Bearer <token>`).
- Store the JWT subject (the user's id) in a `ThreadLocal` holder (e.g. `UserContext`), set in the security/JWT filter and always cleared in a `finally` block. Also put it in MDC for logging.
- When user-specific data is needed, read the user-id from that holder; never accept it from request params/body for authorization purposes.

## MongoDB
- Every Mongo document must have an `@Id` field for efficient fetching.
- If a document has a `userId` field, always fetch/query/update/delete it by `userId` (scoped to the authenticated user from the `ThreadLocal` holder).
