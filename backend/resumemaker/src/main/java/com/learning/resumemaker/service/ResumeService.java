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

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequiredArgsConstructor
@Service
public class ResumeService {

	private final ResumeRepository repository;
	private final ResumeMapper mapper;
	private final AtsService atsService;
	private final Clock clock;

	/** Saves a new resume (built in the UI wizard or parsed from an upload); MongoDB assigns the id. */
	public ResumeResponse create(String userId, ResumeRequest request) {
		Instant now = clock.instant();
		var saved = repository.save(prepare(userId, null, request, now, now, null));
		log.info("Resume {} created in database", saved.getId());
		return mapper.toResponse(saved);
	}

	/** Replaces an existing resume; the id comes from the path, never the body. */
	public ResumeResponse update(String userId, String id, ResumeRequest request) {
		var existing = repository.findByIdAndUserId(id, userId).orElseThrow(() -> {
			log.warn("Update rejected: resume {} not found", id);
			return new ResumeNotFoundException(id);
		});
		var saved = repository.save(prepare(userId, id, request, existing.getCreatedAt(), clock.instant(), existing));
		log.info("Resume {} updated in database", saved.getId());
		return mapper.toResponse(saved);
	}

	public ResumeResponse get(String userId, String id) {
		return mapper.toResponse(repository.findByIdAndUserId(id, userId).orElseThrow(() -> {
			log.warn("Resume {} not found", id);
			return new ResumeNotFoundException(id);
		}));
	}

	/** The user's resumes, most recently saved first. */
	public List<ResumeSummary> list(String userId) {
		List<ResumeSummary> summaries = repository.findByUserId(userId).stream().map(this::summarize)
				.sorted(Comparator.comparing(ResumeSummary::getUpdatedAt, Comparator.nullsLast(Comparator.reverseOrder())))
				.toList();
		log.info("Listed {} resume(s) for user {}", summaries.size(), userId);
		return summaries;
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

	private static String firstNonBlank(String... values) {
		for (String value : values) {
			if (value != null && !value.isBlank()) {
				return value;
			}
		}
		return null;
	}
}
