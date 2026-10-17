package com.learning.resumemaker.model;

import lombok.Builder;

/** Body of the call to the agent service that turns the text of an uploaded resume into a structured resume. */
@Builder
public record ParseRequest(String text) {
}
