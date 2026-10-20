package com.learning.resumemaker.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.learning.resumemaker.model.ResumeTemplate;
import com.learning.resumemaker.service.ResumeTemplateService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

/** The LaTeX templates a resume can be downloaded in. */
@Tag(name = "Templates", description = "LaTeX resume templates")
@RestController
@RequestMapping("/api/templates")
@RequiredArgsConstructor
public class TemplateController {

	private final ResumeTemplateService service;

	/** Lists the available templates. */
	@Operation(summary = "List resume templates")
	@ApiResponse(responseCode = "200", description = "The templates, sorted by name")
	@GetMapping
	public ResponseEntity<List<ResumeTemplate>> listTemplates() {
		return ResponseEntity.ok(service.listTemplates());
	}
}
