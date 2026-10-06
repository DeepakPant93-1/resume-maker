package com.learning.resumemaker.security;

import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.util.Locale;
import java.util.regex.Pattern;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.learning.resumemaker.document.UserDocument;
import com.learning.resumemaker.exception.AuthenticationFailedException;
import com.learning.resumemaker.exception.EmailAlreadyUsedException;
import com.learning.resumemaker.exception.InvalidRequestException;
import com.learning.resumemaker.repository.UserRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** Registers users, checks logins and hands out tokens. Users live in MongoDB with a BCrypt hash, never the password. */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

	static final int MIN_PASSWORD_LENGTH = 8;
	static final int MAX_PASSWORD_BYTES = 72; // BCrypt only uses the first 72 bytes, so longer passwords are refused
	private static final Pattern EMAIL = Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");

	private final UserRepository users;
	private final PasswordEncoder passwordEncoder;
	private final JwtService jwtService;
	private final Clock clock;

	/** A hash nobody has the password for. Checking against it keeps an unknown email as slow as a wrong password. */
	private String decoyHash;

	public AuthResponse register(RegisterRequest request) {
		String email = normalize(request == null ? null : request.getEmail());
		String password = request == null ? null : request.getPassword();
		if (!EMAIL.matcher(email).matches()) {
			log.warn("Registration rejected: '{}' is not a valid email address", email);
			throw new InvalidRequestException("Please enter a valid email address");
		}
		if (password == null || password.length() < MIN_PASSWORD_LENGTH) {
			log.warn("Registration rejected for {}: the password is shorter than {} characters", email, MIN_PASSWORD_LENGTH);
			throw new InvalidRequestException("The password must be at least " + MIN_PASSWORD_LENGTH + " characters");
		}
		if (password.getBytes(StandardCharsets.UTF_8).length > MAX_PASSWORD_BYTES) {
			log.warn("Registration rejected for {}: the password is longer than {} bytes", email, MAX_PASSWORD_BYTES);
			throw new InvalidRequestException("The password is too long (at most " + MAX_PASSWORD_BYTES + " bytes)");
		}
		if (users.existsByEmail(email)) {
			log.warn("Registration rejected: an account already exists for {}", email);
			throw new EmailAlreadyUsedException("An account with this email already exists");
		}

		Instant now = clock.instant();
		String name = request.getName() == null || request.getName().isBlank() ? email.substring(0, email.indexOf('@'))
				: request.getName().strip();
		UserDocument user;
		try {
			user = users.save(UserDocument.builder().email(email).name(name).passwordHash(passwordEncoder.encode(password))
					.createdAt(now).lastLoginAt(now).build());
		} catch (DuplicateKeyException e) { // two sign-ups racing past the check above: the unique index decides
			log.warn("Registration rejected: {} was registered by a concurrent request", email);
			throw new EmailAlreadyUsedException("An account with this email already exists");
		}
		log.info("User {} registered ({})", user.getId(), email);
		return respond(user);
	}

	public AuthResponse login(LoginRequest request) {
		String email = normalize(request == null ? null : request.getEmail());
		String password = request == null || request.getPassword() == null ? "" : request.getPassword();
		UserDocument user = users.findByEmail(email).orElse(null);
		// Same message and same work for "no such user" and "wrong password", so neither can be told apart.
		boolean valid = passwordEncoder.matches(password, user == null ? decoy() : user.getPasswordHash()) && user != null;
		if (!valid) {
			log.warn("Login failed for {}", email);
			throw new AuthenticationFailedException("Invalid email or password");
		}
		user.setLastLoginAt(clock.instant());
		users.save(user);
		log.info("User {} logged in", user.getId());
		return respond(user);
	}

	public UserProfile profile(String userId) {
		return users.findById(userId).map(AuthService::toProfile).orElseThrow(() -> {
			log.warn("A valid token belongs to user {}, who no longer exists", userId);
			return new AuthenticationFailedException("This account no longer exists");
		});
	}

	private AuthResponse respond(UserDocument user) {
		JwtService.IssuedToken token = jwtService.issue(user);
		return AuthResponse.builder().token(token.value()).expiresAt(token.expiresAt()).user(toProfile(user)).build();
	}

	private static UserProfile toProfile(UserDocument user) {
		return UserProfile.builder().id(user.getId()).email(user.getEmail()).name(user.getName()).build();
	}

	private static String normalize(String email) {
		return email == null ? "" : email.strip().toLowerCase(Locale.ROOT);
	}

	private synchronized String decoy() {
		if (decoyHash == null) {
			decoyHash = passwordEncoder.encode("decoy-password-nobody-has");
		}
		return decoyHash;
	}
}
