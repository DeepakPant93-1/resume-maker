package com.learning.resumemaker.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.learning.resumemaker.document.ResumeDocument;

public interface ResumeRepository extends MongoRepository<ResumeDocument, String> {

	List<ResumeDocument> findByUserId(String userId);

	/** A resume only if it belongs to that user: another user's resume looks exactly like one that does not exist. */
	Optional<ResumeDocument> findByIdAndUserId(String id, String userId);
}
