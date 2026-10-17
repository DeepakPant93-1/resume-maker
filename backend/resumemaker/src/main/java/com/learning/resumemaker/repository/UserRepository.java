package com.learning.resumemaker.repository;

import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.learning.resumemaker.document.UserDocument;

public interface UserRepository extends MongoRepository<UserDocument, String> {

	Optional<UserDocument> findByEmail(String email);

	boolean existsByEmail(String email);
}
