package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.ResumeNotFoundException;
import com.learning.resumemaker.mapper.ResumeMapper;
import com.learning.resumemaker.model.Metadata;
import com.learning.resumemaker.model.Profile;
import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.ResumeSummary;
import com.learning.resumemaker.repository.ResumeRepository;

@ExtendWith(MockitoExtension.class)
class ResumeServiceTest {

	private static final Instant NOW = Instant.parse("2026-10-06T10:00:00Z");
	private static final Instant EARLIER = Instant.parse("2026-10-01T09:00:00Z");

	@Mock
	ResumeRepository repository;
	@Mock
	AtsService atsService;

	private ResumeService service() {
		return new ResumeService(repository, new ResumeMapper(), atsService, Clock.fixed(NOW, ZoneOffset.UTC));
	}

	private ResumeRequest request() {
		return ResumeRequest.builder().profile(Profile.builder().fullName("Suraj").jobTitle("Backend Engineer").build())
				.build();
	}

	/** save() returns what it is given, with an id assigned the way MongoDB would. */
	private void saveEchoesWithId() {
		when(repository.save(any())).thenAnswer(call -> {
			ResumeDocument saved = call.getArgument(0);
			if (saved.getId() == null) {
				saved.setId("new-id");
			}
			return saved;
		});
	}

	private ResumeDocument saved() {
		ArgumentCaptor<ResumeDocument> captor = ArgumentCaptor.forClass(ResumeDocument.class);
		verify(repository).save(captor.capture());
		return captor.getValue();
	}

	@Test
	void createStampsTheTimesAndStoresTheServerComputedScore() {
		saveEchoesWithId();
		when(atsService.scoreOrNull(any())).thenReturn(77);
		// a client-supplied score is ignored: the server owns it
		ResumeRequest request = ResumeRequest.builder().profile(request().getProfile())
				.metadata(Metadata.builder().atsScore(1).title("My title").build()).build();

		ResumeResponse response = service().create("u1", request);

		ResumeDocument document = saved();
		assertThat(response.getId()).isEqualTo("new-id");
		assertThat(saved().getUserId()).isEqualTo("u1"); // the new resume belongs to the caller
		assertThat(document.getMetadata().getAtsScore()).isEqualTo(77);
		assertThat(document.getMetadata().getTitle()).isEqualTo("My title");
		assertThat(document.getCreatedAt()).isEqualTo(NOW);
		assertThat(document.getUpdatedAt()).isEqualTo(NOW);
	}

	@Test
	void createStillSavesWhenTheScoreCannotBeComputed() {
		saveEchoesWithId();
		when(atsService.scoreOrNull(any())).thenReturn(null);

		service().create("u1", request());

		assertThat(saved().getMetadata().getAtsScore()).isNull();
	}

	@Test
	void updateKeepsTheCreationTimeAndRefreshesTheUpdateTime() {
		ResumeDocument existing = ResumeDocument.builder().id("r1").createdAt(EARLIER).updatedAt(EARLIER).build();
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(existing));
		saveEchoesWithId();
		when(atsService.scoreOrNull(any())).thenReturn(90);

		service().update("u1", "r1", request());

		ResumeDocument document = saved();
		assertThat(document.getId()).isEqualTo("r1");
		assertThat(document.getCreatedAt()).isEqualTo(EARLIER);
		assertThat(document.getUpdatedAt()).isEqualTo(NOW);
		assertThat(document.getMetadata().getAtsScore()).isEqualTo(90);
	}

	@Test
	void updateKeepsTheLastKnownScoreWhenScoringFails() {
		ResumeDocument existing = ResumeDocument.builder().id("r1").createdAt(EARLIER)
				.metadata(ResumeDocument.Metadata.builder().atsScore(64).build()).build();
		when(repository.findByIdAndUserId("r1", "u1")).thenReturn(Optional.of(existing));
		saveEchoesWithId();
		when(atsService.scoreOrNull(any())).thenReturn(null);

		service().update("u1", "r1", request());

		assertThat(saved().getMetadata().getAtsScore()).isEqualTo(64);
	}

	@Test
	void updateAndGetFailForAnUnknownResume() {
		when(repository.findByIdAndUserId("nope", "u1")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().update("u1", "nope", request())).isInstanceOf(ResumeNotFoundException.class);
		assertThatThrownBy(() -> service().get("u1", "nope")).isInstanceOf(ResumeNotFoundException.class);
		verify(repository, never()).save(any());
	}

	@Test
	void listIsNewestFirstWithUndatedLastAndAReadableTitleForEachResume() {
		when(repository.findByUserId("u1")).thenReturn(List.of(
				ResumeDocument.builder().id("old").updatedAt(EARLIER)
						.profile(ResumeDocument.Profile.builder().fullName("Only Name").build()).build(),
				ResumeDocument.builder().id("undated").build(),
				ResumeDocument.builder().id("new").updatedAt(NOW)
						.metadata(ResumeDocument.Metadata.builder().title("Chosen").atsScore(88).build())
						.profile(ResumeDocument.Profile.builder().jobTitle("Ignored").build()).build(),
				ResumeDocument.builder().id("role").updatedAt(NOW.minusSeconds(60))
						.profile(ResumeDocument.Profile.builder().jobTitle("Platform Engineer").fullName("X").build())
						.build()));

		List<ResumeSummary> list = service().list("u1");

		assertThat(list).extracting(ResumeSummary::getId).containsExactly("new", "role", "old", "undated");
		assertThat(list).extracting(ResumeSummary::getTitle)
				.containsExactly("Chosen", "Platform Engineer", "Only Name", "Untitled resume");
		assertThat(list.get(0).getAtsScore()).isEqualTo(88);
		assertThat(list.get(1).getAtsScore()).isNull();
	}

	@Test
	void anotherUsersResumeLooksLikeOneThatDoesNotExist() {
		when(repository.findByIdAndUserId("r1", "intruder")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().get("intruder", "r1")).isInstanceOf(ResumeNotFoundException.class);
		assertThatThrownBy(() -> service().update("intruder", "r1", request())).isInstanceOf(ResumeNotFoundException.class);
		verify(repository, never()).save(any());
	}
}
