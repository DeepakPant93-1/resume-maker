package com.learning.resumemaker.security;

import com.learning.resumemaker.exception.AuthenticationFailedException;

/** Holds the id of the signed-in user (the JWT subject) for the current request thread. */
public final class UserContext {

	private static final ThreadLocal<String> USER_ID = new ThreadLocal<>();

	private UserContext() {
	}

	/** Stores the user id for the current thread. */
	public static void setUserId(String userId) {
		USER_ID.set(userId);
	}

	/** The user id of the current request, or null if there is none. */
	public static String getUserId() {
		return USER_ID.get();
	}

	/**
	 * The user id of the current request.
	 *
	 * @throws AuthenticationFailedException if nobody is signed in
	 */
	public static String requireUserId() {
		String userId = USER_ID.get();
		if (userId == null) {
			throw new AuthenticationFailedException("Please log in again: the login token is missing, invalid or expired");
		}
		return userId;
	}

	/** Removes the user id from the current thread; always call it when the request ends. */
	public static void clear() {
		USER_ID.remove();
	}
}
