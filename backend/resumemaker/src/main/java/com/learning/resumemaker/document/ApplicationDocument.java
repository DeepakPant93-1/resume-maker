package com.learning.resumemaker.document;

import java.time.Instant;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import com.learning.resumemaker.model.ApplicationStage;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Database representation of a tracked job application (MongoDB collection "applications"). */
@Document(collection = "applications")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApplicationDocument {

	@Id
	private String id;
	/** The user who owns this application (the subject of their login token). */
	@Indexed
	private String userId;
	private String company;
	private String role;
	private String resumeId;
	private ApplicationStage stage;
	private Instant createdAt;
	private Instant updatedAt;
}
