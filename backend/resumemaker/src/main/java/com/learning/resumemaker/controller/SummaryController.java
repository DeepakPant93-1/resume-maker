package com.learning.resumemaker.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.SummaryRequest;
import com.learning.resumemaker.model.SummaryResponse;
import com.learning.resumemaker.service.SummaryService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** The editor's "Write with AI" button: writes or improves the professional summary. */
@Slf4j
@RestController
@RequestMapping("/api/summary")
@RequiredArgsConstructor
public class SummaryController {

	private final SummaryService service;

	@PostMapping
	public SummaryResponse write(@RequestBody SummaryRequest request) {
		log.info("POST /api/summary");
		return service.write(request);
	}
}
