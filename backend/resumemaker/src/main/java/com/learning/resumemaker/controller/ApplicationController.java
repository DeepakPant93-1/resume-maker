package com.learning.resumemaker.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.ApplicationRequest;
import com.learning.resumemaker.model.ApplicationResponse;
import com.learning.resumemaker.service.ApplicationService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

/** The signed-in user's job application tracker. */
@Tag(name = "Applications", description = "The signed-in user's job applications")
@RestController
@RequestMapping("/api/applications")
@RequiredArgsConstructor
public class ApplicationController {

	private final ApplicationService service;

	/** Lists the user's applications, most recently changed first. */
	@Operation(summary = "List my applications")
	@ApiResponse(responseCode = "200", description = "The applications")
	@GetMapping
	public ResponseEntity<List<ApplicationResponse>> list() {
		return ResponseEntity.ok(service.list());
	}

	/** Starts tracking an application. */
	@Operation(summary = "Track an application")
	@ApiResponse(responseCode = "201", description = "The saved application")
	@ApiResponse(responseCode = "400", description = "Invalid application")
	@PostMapping
	public ResponseEntity<ApplicationResponse> create(@Valid @RequestBody ApplicationRequest request) {
		return ResponseEntity.status(HttpStatus.CREATED).body(service.create(request));
	}

	/** Replaces an application (for example to move it to the next stage). */
	@Operation(summary = "Update an application")
	@ApiResponse(responseCode = "200", description = "The saved application")
	@ApiResponse(responseCode = "404", description = "No such application")
	@PutMapping("/{id}")
	public ResponseEntity<ApplicationResponse> update(@PathVariable String id,
			@Valid @RequestBody ApplicationRequest request) {
		return ResponseEntity.ok(service.update(id, request));
	}

	/** Stops tracking an application. */
	@Operation(summary = "Delete an application")
	@ApiResponse(responseCode = "204", description = "Deleted")
	@ApiResponse(responseCode = "404", description = "No such application")
	@DeleteMapping("/{id}")
	public ResponseEntity<Void> delete(@PathVariable String id) {
		service.delete(id);
		return ResponseEntity.noContent().build();
	}
}
