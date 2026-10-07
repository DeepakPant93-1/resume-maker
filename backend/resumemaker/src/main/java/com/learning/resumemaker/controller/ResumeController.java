package com.learning.resumemaker.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.learning.resumemaker.model.ResumeRequest;
import com.learning.resumemaker.model.ResumeResponse;
import com.learning.resumemaker.model.ResumeSummary;
import com.learning.resumemaker.service.ResumeService;
import com.learning.resumemaker.service.ResumeUploadService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
		
@RequiredArgsConstructor
@Slf4j
@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

	private final ResumeService service;
	private final ResumeUploadService uploadService;

	@PostMapping(path = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public ResumeResponse upload(@AuthenticationPrincipal Jwt jwt, @RequestPart("file") MultipartFile file) {
		log.info("POST /api/resumes/upload - file='{}', size={} bytes", file.getOriginalFilename(), file.getSize());
		ResumeResponse response = uploadService.upload(jwt.getSubject(), file);
		log.info("POST /api/resumes/upload - completed, resumeId={}", response.getId());
		return response;
	}

	@GetMapping
	public List<ResumeSummary> list(@AuthenticationPrincipal Jwt jwt) {
		log.info("GET /api/resumes");
		return service.list(jwt.getSubject());
	}

	@GetMapping("/{id}")
	public ResumeResponse get(@AuthenticationPrincipal Jwt jwt, @PathVariable String id) {
		log.info("GET /api/resumes/{}", id);
		return service.get(jwt.getSubject(), id);
	}

	@PostMapping
	@ResponseStatus(HttpStatus.CREATED)
	public ResumeResponse create(@AuthenticationPrincipal Jwt jwt, @RequestBody ResumeRequest request) {
		log.info("POST /api/resumes - create requested");
		ResumeResponse response = service.create(jwt.getSubject(), request);
		log.info("POST /api/resumes - completed, resumeId={}", response.getId());
		return response;
	}

	@PutMapping("/{id}")
	public ResumeResponse update(@AuthenticationPrincipal Jwt jwt, @PathVariable String id,
			@RequestBody ResumeRequest request) {
		log.info("PUT /api/resumes/{} - update requested", id);
		ResumeResponse response = service.update(jwt.getSubject(), id, request);
		log.info("PUT /api/resumes/{} - completed", id);
		return response;
	}
}
