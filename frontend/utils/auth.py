"""Who is logged in: the login token and user, kept in this browser session's state and in a browser cookie.

Streamlit's session state is per browser tab connection, so a page refresh starts a new session and would log the
user out. To survive a refresh the token is also kept in a cookie (`resuai_token`) that expires together with the
token. On a new session the app reads that cookie and asks the backend whether the token is still valid.

The cookie is written by JavaScript, so it cannot be HttpOnly: script running in the page could read it. It is
SameSite=Strict (never sent from other sites) and Secure when the page is served over HTTPS.
"""
import json

import streamlit as st
import streamlit.components.v1 as components

TOKEN_KEY = "auth_token"
COOKIE = "resuai_token"
_WRITE_COOKIE = "_cookie_write"      # (token, expires_at) waiting to be written to the browser
_CLEAR_COOKIE = "_cookie_clear"      # the browser cookie must be removed
_RESTORE_DONE = "_restore_attempted"  # at most one cookie login attempt per session


def is_authenticated():
    return bool(st.session_state.get(TOKEN_KEY))


def token():
    """The login token to send as `Authorization: Bearer ...`, or None when nobody is logged in."""
    return st.session_state.get(TOKEN_KEY)


def sign_in(auth_response, remember=True):
    """Remember the backend's login/registration response (token + user) for this session.

    With `remember`, the token is also queued to be written to the browser cookie on the next render.
    """
    user = auth_response["user"]
    st.session_state[TOKEN_KEY] = auth_response["token"]
    st.session_state.user = {
        "id": user["id"],
        "email": user["email"],
        "name": user.get("name") or user["email"],
        "role": "",       # the Settings page lets people fill these in; they are not stored in the backend yet
        "location": "",
    }
    if remember and auth_response.get("expires_at"):
        st.session_state[_WRITE_COOKIE] = (auth_response["token"], auth_response["expires_at"])
        st.session_state.pop(_CLEAR_COOKIE, None)


def sign_out(notice=None, forget_cookie=True):
    """Forget everything from this session (token, user, open resume...) so the next person starts clean."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # `st.context.cookies` is a snapshot from when this session connected, so it still holds the old token: never
    # log back in from it during this session.
    st.session_state[_RESTORE_DONE] = True
    if forget_cookie:
        st.session_state[_CLEAR_COOKIE] = True
    if notice:
        st.session_state["login_notice"] = notice


def saved_token():
    """The token cookie the browser sent when this session connected, or None."""
    try:
        return st.context.cookies.get(COOKIE)
    except Exception:  # noqa: BLE001 - no cookie support (old Streamlit, or not running in a browser session)
        return None


def restore_attempted():
    return bool(st.session_state.get(_RESTORE_DONE))


def mark_restore_attempted():
    st.session_state[_RESTORE_DONE] = True


def forget_cookie():
    """Remove the browser cookie on the next render (for example when it holds a token that has expired)."""
    st.session_state[_CLEAR_COOKIE] = True


def flush_cookie():
    """Write or remove the browser cookie if a change is pending. Call once per run, before anything else renders."""
    write = st.session_state.pop(_WRITE_COOKIE, None)
    clear = st.session_state.pop(_CLEAR_COOKIE, False)
    if write:
        token_value, expires_at = write
        expires_at = expires_at.split(".")[0].rstrip("Z") + "Z"  # JavaScript's Date parses whole seconds everywhere
        script = (
            f"const secure = location.protocol === 'https:' ? '; Secure' : '';"
            f"document.cookie = {json.dumps(COOKIE)} + '=' + {json.dumps(token_value)}"
            f" + '; expires=' + new Date({json.dumps(expires_at)}).toUTCString() + '; path=/; SameSite=Strict' + secure;"
        )
    elif clear:
        script = f"document.cookie = {json.dumps(COOKIE)} + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Strict';"
    else:
        return
    components.html(f"<script>{script}</script>", height=0)
