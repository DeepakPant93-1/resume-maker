package com.learning.resumemaker.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.service.AtsService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

/** ATS check of a resume (saved or not). The scoring itself happens in the agent service. */
@Tag(name = "ATS", description = "Applicant tracking system score")
@RestController
@RequestMapping("/api/ats")
@RequiredArgsConstructor
public class AtsController {

	private final AtsService service;

	/** Scores the resume as sent. */
	@Operation(summary = "Score a resume for ATS")
	@ApiResponse(responseCode = "200", description = "The score report")
	@ApiResponse(responseCode = "503", description = "Agent service not reachable")
	@PostMapping
	public ResponseEntity<AtsReport> checkResume(@Valid @RequestBody AtsRequest request) {
		return ResponseEntity.ok(service.checkResume(request));
	}
}
