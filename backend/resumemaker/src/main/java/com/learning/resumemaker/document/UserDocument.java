package com.learning.resumemaker.document;

import java.time.Instant;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** A registered user (MongoDB collection "users"). Only a BCrypt hash of the password is ever stored. */
@Document(collection = "users")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDocument {

	@Id
	private String id;
	/** Lower-cased; unique. */
	@Indexed(unique = true)
	private String email;
	private String name;
	private String passwordHash;
	private Instant createdAt;
	private Instant lastLoginAt;
}
