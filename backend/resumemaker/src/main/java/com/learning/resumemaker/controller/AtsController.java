package com.learning.resumemaker.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.AtsReport;
import com.learning.resumemaker.model.AtsRequest;
import com.learning.resumemaker.service.AtsService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/** ATS check of a resume (saved or not). The scoring itself happens in the agent service. */
@Slf4j
@RestController
@RequestMapping("/api/ats")
@RequiredArgsConstructor
public class AtsController {

	private final AtsService service;

	@PostMapping
	public AtsReport check(@RequestBody AtsRequest request) {
		log.info("POST /api/ats");
		return service.check(request);
	}
}
