package com.learning.resumemaker.security;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.learning.resumemaker.document.UserDocument;
import com.learning.resumemaker.exception.AuthenticationFailedException;
import com.learning.resumemaker.exception.EmailAlreadyUsedException;
import com.learning.resumemaker.exception.InvalidRequestException;
import com.learning.resumemaker.repository.UserRepository;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

	private static final Instant NOW = Instant.parse("2026-10-06T10:00:00Z");

	@Mock
	UserRepository users;
	@Mock
	JwtService jwtService;
	private final PasswordEncoder encoder = new BCryptPasswordEncoder(4); // cheap rounds keep the tests fast

	private AuthService service() {
		return new AuthService(users, encoder, jwtService, Clock.fixed(NOW, ZoneOffset.UTC));
	}

	private void tokenIsIssued() {
		when(jwtService.issue(any())).thenReturn(new JwtService.IssuedToken("signed-token", NOW.plusSeconds(3600)));
	}

	private UserDocument stored(String password) {
		return UserDocument.builder().id("u1").email("suraj@example.com").name("Suraj")
				.passwordHash(encoder.encode(password)).createdAt(NOW.minusSeconds(86400)).build();
	}

	@Test
	void registerStoresALowercaseEmailAndAHashNeverThePassword() {
		tokenIsIssued();
		when(users.existsByEmail("suraj@example.com")).thenReturn(false);
		when(users.save(any())).thenAnswer(call -> {
			UserDocument saved = call.getArgument(0);
			saved.setId("u1");
			return saved;
		});

		AuthResponse response = service().register(new RegisterRequest("  Suraj ", " Suraj@Example.COM ", "correct horse"));

		ArgumentCaptor<UserDocument> saved = ArgumentCaptor.forClass(UserDocument.class);
		verify(users).save(saved.capture());
		UserDocument user = saved.getValue();
		assertThat(user.getEmail()).isEqualTo("suraj@example.com");
		assertThat(user.getName()).isEqualTo("Suraj");
		assertThat(user.getPasswordHash()).isNotEqualTo("correct horse").startsWith("$2");
		assertThat(encoder.matches("correct horse", user.getPasswordHash())).isTrue();
		assertThat(user.getCreatedAt()).isEqualTo(NOW);
		assertThat(user.getLastLoginAt()).isEqualTo(NOW);
		assertThat(response.getToken()).isEqualTo("signed-token");
		assertThat(response.getUser().getId()).isEqualTo("u1");
		assertThat(response.toString()).doesNotContain(user.getPasswordHash());
	}

	@Test
	void theNameDefaultsToTheStartOfTheEmail() {
		tokenIsIssued();
		when(users.save(any())).thenAnswer(call -> call.getArgument(0));

		AuthResponse response = service().register(new RegisterRequest(null, "priya@example.com", "long enough"));

		assertThat(response.getUser().getName()).isEqualTo("priya");
	}

	@Test
	void registerRejectsABadEmailAShortPasswordAndATooLongPasswordWithoutSavingAnything() {
		assertThatThrownBy(() -> service().register(new RegisterRequest("A", "not-an-email", "long enough")))
				.isInstanceOf(InvalidRequestException.class).hasMessageContaining("email");
		assertThatThrownBy(() -> service().register(new RegisterRequest("A", "a@example.com", "short")))
				.isInstanceOf(InvalidRequestException.class).hasMessageContaining("at least 8");
		assertThatThrownBy(() -> service().register(new RegisterRequest("A", "a@example.com", "x".repeat(73))))
				.isInstanceOf(InvalidRequestException.class).hasMessageContaining("too long");
		assertThatThrownBy(() -> service().register(null)).isInstanceOf(InvalidRequestException.class);
		verifyNoInteractions(jwtService);
		verify(users, never()).save(any());
	}

	@Test
	void anEmailThatIsAlreadyRegisteredIsRefusedEvenIfTheCaseDiffers() {
		when(users.existsByEmail("suraj@example.com")).thenReturn(true);

		assertThatThrownBy(() -> service().register(new RegisterRequest("S", "SURAJ@example.com", "long enough")))
				.isInstanceOf(EmailAlreadyUsedException.class);
		verify(users, never()).save(any());
	}

	@Test
	void twoSignUpsRacingPastTheCheckAreStoppedByTheUniqueIndex() {
		when(users.save(any())).thenThrow(new DuplicateKeyException("duplicate"));

		assertThatThrownBy(() -> service().register(new RegisterRequest("S", "suraj@example.com", "long enough")))
				.isInstanceOf(EmailAlreadyUsedException.class);
	}

	@Test
	void loginReturnsATokenAndRecordsTheLoginTime() {
		tokenIsIssued();
		UserDocument user = stored("correct horse");
		when(users.findByEmail("suraj@example.com")).thenReturn(Optional.of(user));

		AuthResponse response = service().login(new LoginRequest(" SURAJ@example.com ", "correct horse"));

		assertThat(response.getToken()).isEqualTo("signed-token");
		assertThat(response.getUser().getEmail()).isEqualTo("suraj@example.com");
		assertThat(user.getLastLoginAt()).isEqualTo(NOW);
		verify(users).save(user);
	}

	@Test
	void aWrongPasswordAndAnUnknownEmailFailIdentically() {
		when(users.findByEmail("suraj@example.com")).thenReturn(Optional.of(stored("correct horse")));
		when(users.findByEmail("nobody@example.com")).thenReturn(Optional.empty());

		Throwable wrongPassword = org.assertj.core.api.Assertions
				.catchThrowable(() -> service().login(new LoginRequest("suraj@example.com", "wrong password")));
		Throwable unknownEmail = org.assertj.core.api.Assertions
				.catchThrowable(() -> service().login(new LoginRequest("nobody@example.com", "correct horse")));

		assertThat(wrongPassword).isInstanceOf(AuthenticationFailedException.class);
		assertThat(unknownEmail).isInstanceOf(AuthenticationFailedException.class);
		assertThat(wrongPassword.getMessage()).isEqualTo(unknownEmail.getMessage()).isEqualTo("Invalid email or password");
		verifyNoInteractions(jwtService);
		verify(users, never()).save(any());
	}

	@Test
	void profileOfADeletedUserIsRefused() {
		when(users.findById("gone")).thenReturn(Optional.empty());

		assertThatThrownBy(() -> service().profile("gone")).isInstanceOf(AuthenticationFailedException.class);
	}
}
