package com.learning.resumemaker.service;

import java.time.Clock;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.ApplicationDocument;
import com.learning.resumemaker.exception.ApplicationNotFoundException;
import com.learning.resumemaker.model.ApplicationRequest;
import com.learning.resumemaker.model.ApplicationResponse;
import com.learning.resumemaker.model.ApplicationStage;
import com.learning.resumemaker.repository.ApplicationRepository;
import com.learning.resumemaker.security.UserContext;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Tracks the signed-in user's job applications. Every query is scoped to that user. */
@Slf4j
@RequiredArgsConstructor
@Service
public class ApplicationService {

	private final ApplicationRepository repository;
	private final Clock clock;

	/** Starts tracking an application; MongoDB assigns the id. */
	public ApplicationResponse create(ApplicationRequest request) {
		Instant now = clock.instant();
		var saved = repository.save(toDocument(null, UserContext.requireUserId(), request, now, now));
		log.info("Application {} created", saved.getId());
		return toResponse(saved);
	}

	/** Replaces an application; the id comes from the path, never the body. */
	public ApplicationResponse update(String id, ApplicationRequest request) {
		String userId = UserContext.requireUserId();
		var existing = findOwned(userId, id);
		var saved = repository.save(toDocument(id, userId, request, existing.getCreatedAt(), clock.instant()));
		log.info("Application {} updated", saved.getId());
		return toResponse(saved);
	}

	/** Deletes one of the signed-in user's applications. */
	public void delete(String id) {
		repository.delete(findOwned(UserContext.requireUserId(), id));
		log.info("Application {} deleted", id);
	}

	/** The signed-in user's applications, most recently changed first. */
	public List<ApplicationResponse> list() {
		List<ApplicationResponse> applications = repository.findByUserId(UserContext.requireUserId()).stream()
				.map(this::toResponse)
				.sorted(Comparator.comparing(ApplicationResponse::updatedAt,
						Comparator.nullsLast(Comparator.reverseOrder())))
				.toList();
		log.info("Listed {} application(s)", applications.size());
		return applications;
	}

	private ApplicationDocument findOwned(String userId, String id) {
		return repository.findByIdAndUserId(id, userId).orElseThrow(() -> new ApplicationNotFoundException(id));
	}

	private ApplicationDocument toDocument(String id, String userId, ApplicationRequest r, Instant createdAt,
			Instant updatedAt) {
		return ApplicationDocument.builder()
				.id(id)
				.userId(userId)
				.company(r.company().trim())
				.role(r.role().trim())
				.resumeId(r.resumeId() == null || r.resumeId().isBlank() ? null : r.resumeId())
				.stage(r.stage() != null ? r.stage() : ApplicationStage.APPLIED)
				.createdAt(createdAt)
				.updatedAt(updatedAt)
				.build();
	}

	private ApplicationResponse toResponse(ApplicationDocument d) {
		return ApplicationResponse.builder()
				.id(d.getId())
				.company(d.getCompany())
				.role(d.getRole())
				.resumeId(d.getResumeId())
				.stage(d.getStage())
				.createdAt(d.getCreatedAt())
				.updatedAt(d.getUpdatedAt())
				.build();
	}
}
