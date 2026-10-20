package com.learning.resumemaker.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.learning.resumemaker.document.ApplicationDocument;

public interface ApplicationRepository extends MongoRepository<ApplicationDocument, String> {

	List<ApplicationDocument> findByUserId(String userId);

	/** An application only if it belongs to that user: another user's looks exactly like one that does not exist. */
	Optional<ApplicationDocument> findByIdAndUserId(String id, String userId);
}
