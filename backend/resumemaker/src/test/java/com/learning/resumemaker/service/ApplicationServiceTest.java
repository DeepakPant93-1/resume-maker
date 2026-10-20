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

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.learning.resumemaker.document.ApplicationDocument;
import com.learning.resumemaker.exception.ApplicationNotFoundException;
import com.learning.resumemaker.model.ApplicationRequest;
import com.learning.resumemaker.model.ApplicationResponse;
import com.learning.resumemaker.model.ApplicationStage;
import com.learning.resumemaker.repository.ApplicationRepository;
import com.learning.resumemaker.security.UserContext;

@ExtendWith(MockitoExtension.class)
class ApplicationServiceTest {

	private static final Instant NOW = Instant.parse("2026-10-06T10:00:00Z");
	private static final Instant EARLIER = Instant.parse("2026-10-01T09:00:00Z");

	@Mock
	ApplicationRepository repository;

	@BeforeEach
	void signIn() {
		UserContext.setUserId("u1");
	}

	@AfterEach
	void signOut() {
		UserContext.clear();
	}

	private ApplicationService service() {
		return new ApplicationService(repository, Clock.fixed(NOW, ZoneOffset.UTC));
	}

	private ApplicationDocument saved() {
		ArgumentCaptor<ApplicationDocument> captor = ArgumentCaptor.forClass(ApplicationDocument.class);
		verify(repository).save(captor.capture());
		return captor.getValue();
	}

	@Test
	void createStoresTheApplicationForTheSignedInUserAsApplied() {
		when(repository.save(any())).thenAnswer(call -> {
			ApplicationDocument d = call.getArgument(0);
			d.setId("a1");
			return d;
		});

		ApplicationResponse response = service()
				.create(ApplicationRequest.builder().company("  Acme ").role("Java Dev").resumeId(" ").build());

		ApplicationDocument document = saved();
		assertThat(document.getUserId()).isEqualTo("u1");
		assertThat(document.getCompany()).isEqualTo("Acme");
		assertThat(document.getStage()).isEqualTo(ApplicationStage.APPLIED);
		assertThat(document.getResumeId()).isNull();
		assertThat(document.getCreatedAt()).isEqualTo(NOW);
		assertThat(response.id()).isEqualTo("a1");
	}

	@Test
	void updateKeepsTheIdAndCreationTimeAndMovesTheStage() {
		ApplicationDocument existing = ApplicationDocument.builder().id("a1").userId("u1").createdAt(EARLIER).build();
		when(repository.findByIdAndUserId("a1", "u1")).thenReturn(Optional.of(existing));
		when(repository.save(any())).thenAnswer(call -> call.getArgument(0));

		service().update("a1", ApplicationRequest.builder().company("Acme").role("Dev")
				.stage(ApplicationStage.INTERVIEW).build());

		ApplicationDocument document = saved();
		assertThat(document.getId()).isEqualTo("a1");
		assertThat(document.getCreatedAt()).isEqualTo(EARLIER);
		assertThat(document.getUpdatedAt()).isEqualTo(NOW);
		assertThat(document.getStage()).isEqualTo(ApplicationStage.INTERVIEW);
	}

	@Test
	void listIsNewestFirst() {
		when(repository.findByUserId("u1")).thenReturn(List.of(
				ApplicationDocument.builder().id("old").updatedAt(EARLIER).build(),
				ApplicationDocument.builder().id("new").updatedAt(NOW).build()));

		assertThat(service().list()).extracting(ApplicationResponse::id).containsExactly("new", "old");
	}

	@Test
	void deleteAndUpdateFailForSomeoneElsesOrUnknownApplication() {
		when(repository.findByIdAndUserId("nope", "u1")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().delete("nope")).isInstanceOf(ApplicationNotFoundException.class);
		assertThatThrownBy(() -> service().update("nope",
				ApplicationRequest.builder().company("A").role("B").build()))
				.isInstanceOf(ApplicationNotFoundException.class);
		verify(repository, never()).delete(any());
		verify(repository, never()).save(any());
	}
}
