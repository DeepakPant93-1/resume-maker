package com.learning.resumemaker.config;

import org.springdoc.core.customizers.OperationCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.learning.resumemaker.web.RequestContextInterceptor;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.media.StringSchema;
import io.swagger.v3.oas.models.parameters.HeaderParameter;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;

/** OpenAPI / Swagger settings: API info, the JWT bearer scheme and the optional request-id header. */
@Configuration
public class OpenApiConfig {

	static final String BEARER_SCHEME = "bearerAuth";

	/** Describes the API and declares JWT bearer authentication for every operation. */
	@Bean
	public OpenAPI resumeMakerOpenApi() {
		return new OpenAPI()
				.info(new Info().title("Resume Maker API").version("v1")
						.description("Resumes, ATS scoring and AI summaries"))
				.addSecurityItem(new SecurityRequirement().addList(BEARER_SCHEME))
				.schemaRequirement(BEARER_SCHEME, new SecurityScheme().type(SecurityScheme.Type.HTTP)
						.scheme("bearer").bearerFormat("JWT"));
	}

	/** Documents the optional request-id header on every operation. */
	@Bean
	public OperationCustomizer requestIdHeaderCustomizer() {
		return (operation, handlerMethod) -> operation.addParametersItem(new HeaderParameter()
				.name(RequestContextInterceptor.REQUEST_ID_HEADER).required(false).schema(new StringSchema())
				.description("Optional id to trace the request; a UUID is generated if absent. "
						+ "Returned as the response-id header."));
	}
}
