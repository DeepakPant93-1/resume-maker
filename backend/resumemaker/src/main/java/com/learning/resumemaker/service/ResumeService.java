package com.learning.resumemaker.service;

import java.time.Clock;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;

import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.mapper.ResumeMapper;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.ResumeSummary;
import com.learning.resumemaker.repository.ResumeRepository;
import com.learning.resumemaker.security.UserContext;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Creates, reads and updates the signed-in user's resumes. Every query is scoped to that user. */
@Slf4j
@RequiredArgsConstructor
@Service
public class ResumeService {

	private final ResumeRepository repository;
	private final ResumeMapper mapper;
	private final AtsService atsService;
	private final Clock clock;

	/** Saves a new resume (built in the UI wizard or parsed from an upload); MongoDB assigns the id. */
	public ResumeResponse createResume(ResumeRequest request) {
		Instant now = clock.instant();
		var saved = repository.save(prepare(UserContext.requireUserId(), null, request, now, now, null));
		log.info("Resume {} created", saved.getId());
		return mapper.toResponse(saved);
	}

	/** Replaces an existing resume; the id comes from the path, never the body. */
	public ResumeResponse updateResume(String id, ResumeRequest request) {
		String userId = UserContext.requireUserId();
		var existing = findOwned(userId, id);
		var saved = repository.save(prepare(userId, id, request, existing.getCreatedAt(), clock.instant(), existing));
		log.info("Resume {} updated", saved.getId());
		return mapper.toResponse(saved);
	}

	/** One of the signed-in user's resumes; someone else's looks exactly like one that does not exist. */
	public ResumeResponse getResume(String id) {
		return mapper.toResponse(findOwned(UserContext.requireUserId(), id));
	}

	/** The signed-in user's resumes, most recently saved first. */
	public List<ResumeSummary> listResumes() {
		String userId = UserContext.requireUserId();
		List<ResumeSummary> summaries = repository.findByUserId(userId).stream().map(this::summarize)
				.sorted(Comparator.comparing(ResumeSummary::updatedAt, Comparator.nullsLast(Comparator.reverseOrder())))
				.toList();
		log.info("Listed {} resume(s)", summaries.size());
		return summaries;
	}

	private ResumeDocument findOwned(String userId, String id) {
		return repository.findByIdAndUserId(id, userId).orElseThrow(() -> new ResumeNotFoundException(id));
	}

	/**
	 * The document to store: timestamps set, and the ATS score recomputed. The server owns the score, so one sent
	 * by a client is ignored. If scoring fails, the last known score is kept rather than blanked.
	 */
	private ResumeDocument prepare(String userId, String id, ResumeRequest request, Instant createdAt, Instant updatedAt,
			ResumeDocument previous) {
		ResumeDocument document = mapper.toDocument(id, request);
		document.setUserId(userId);
		Integer score = atsService.scoreOrNull(request);
		if (score == null && previous != null && previous.getMetadata() != null) {
			score = previous.getMetadata().getAtsScore();
		}
		ResumeDocument.Metadata metadata = document.getMetadata() != null ? document.getMetadata()
				: new ResumeDocument.Metadata();
		metadata.setAtsScore(score);
		document.setMetadata(metadata);
		document.setCreatedAt(createdAt);
		document.setUpdatedAt(updatedAt);
		return document;
	}

	/** One dashboard card for a stored resume. */
	private ResumeSummary summarize(ResumeDocument document) {
		var profile = document.getProfile();
		String title = firstNonBlank(
				document.getMetadata() == null ? null : document.getMetadata().getTitle(),
				profile == null ? null : profile.getJobTitle(),
				profile == null ? null : profile.getFullName());
		return ResumeSummary.builder()
				.id(document.getId())
				.title(title != null ? title : "Untitled resume")
				.atsScore(document.getMetadata() == null ? null : document.getMetadata().getAtsScore())
				.updatedAt(document.getUpdatedAt())
				.build();
	}

	/** The first value that has text, or null. */
	private static String firstNonBlank(String... values) {
		for (String value : values) {
			if (value != null && !value.isBlank()) {
				return value;
			}
		}
		return null;
	}
}
