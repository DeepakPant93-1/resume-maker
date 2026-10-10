package com.learning.resumemaker.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;

/** Who the resume is about and how to reach them. */
@Builder
@Schema(description = "Personal details and professional summary")
public record Profile(
		@Size(max = 200) String fullName,
		@Size(max = 200) String jobTitle,
		@Size(max = 254) String email,
		@Size(max = 50) String phone,
		@Size(max = 200) String location,
		@Size(max = 300) String linkedin,
		@Size(max = 5000) String summary) {
}
