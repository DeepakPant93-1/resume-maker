package com.learning.resumemaker.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;
import com.learning.resumemaker.service.SummaryService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

/** The editor's "Write with AI" button: writes or improves the professional summary. */
@Tag(name = "Summary", description = "AI written professional summary")
@RestController
@RequestMapping("/api/summary")
@RequiredArgsConstructor
public class SummaryController {

	private final SummaryService service;

	/** Writes a new summary, or improves the one sent. */
	@Operation(summary = "Write or improve the professional summary")
	@ApiResponse(responseCode = "200", description = "The summary")
	@ApiResponse(responseCode = "503", description = "Agent service not reachable")
	@PostMapping
	public ResponseEntity<SummaryResponse> writeSummary(@Valid @RequestBody SummaryRequest request) {
		return ResponseEntity.ok(service.writeSummary(request));
	}
}
