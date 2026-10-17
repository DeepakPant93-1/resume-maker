package com.learning.resumemaker.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.ResumeSummary;
import com.learning.resumemaker.service.ResumeService;
import com.learning.resumemaker.service.ResumeUploadService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

/** CRUD and PDF upload for the signed-in user's resumes. */
@Tag(name = "Resumes", description = "The signed-in user's resumes")
@RestController
@RequestMapping("/api/resumes")
@RequiredArgsConstructor
public class ResumeController {

	private final ResumeService service;
	private final ResumeUploadService uploadService;

	/** Parses an uploaded PDF into a new resume. */
	@Operation(summary = "Create a resume from a PDF")
	@ApiResponse(responseCode = "200", description = "The parsed and saved resume")
	@ApiResponse(responseCode = "400", description = "Missing, non-PDF or unreadable file")
	@PostMapping(path = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public ResponseEntity<ResumeResponse> uploadResume(@RequestPart("file") MultipartFile file) {
		return ResponseEntity.ok(uploadService.uploadResume(file));
	}

	/** Lists the user's resumes, newest first. */
	@Operation(summary = "List my resumes")
	@ApiResponse(responseCode = "200", description = "The resume cards")
	@GetMapping
	public ResponseEntity<List<ResumeSummary>> listResumes() {
		return ResponseEntity.ok(service.listResumes());
	}

	/** One resume of the user. */
	@Operation(summary = "Get a resume")
	@ApiResponse(responseCode = "200", description = "The resume")
	@ApiResponse(responseCode = "404", description = "No such resume")
	@GetMapping("/{id}")
	public ResponseEntity<ResumeResponse> getResume(@PathVariable String id) {
		return ResponseEntity.ok(service.getResume(id));
	}

	/** Saves a new resume. */
	@Operation(summary = "Create a resume")
	@ApiResponse(responseCode = "201", description = "The saved resume")
	@ApiResponse(responseCode = "400", description = "Invalid resume")
	@PostMapping
	public ResponseEntity<ResumeResponse> createResume(@Valid @RequestBody ResumeRequest request) {
		return ResponseEntity.status(HttpStatus.CREATED).body(service.createResume(request));
	}

	/** Replaces a resume. */
	@Operation(summary = "Update a resume")
	@ApiResponse(responseCode = "200", description = "The saved resume")
	@ApiResponse(responseCode = "404", description = "No such resume")
	@PutMapping("/{id}")
	public ResponseEntity<ResumeResponse> updateResume(@PathVariable String id,
			@Valid @RequestBody ResumeRequest request) {
		return ResponseEntity.ok(service.updateResume(id, request));
	}
}
