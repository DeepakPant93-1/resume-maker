package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

import com.learning.resumemaker.model.ResumeRequest;

class ResumeParserTest {

	private static final String SAMPLE = """
			Suraj Singh Karki
			Senior Software Engineer
			suraj.karki@coredge.io | +91-9800000000 | linkedin.com/in/surajsingh
			Summary
			Results-driven engineer with 5+ years of experience.
			Experience
			Senior Backend Engineer at Coredge  Jan 2023 - Present
			• Led migration to microservices, reducing deployment time by 40%
			• Mentored 2 junior engineers
			Software Engineer
			Previous Company Pvt. Ltd.  Jun 2021 - Dec 2022
			• Built data pipelines processing 1M+ records daily
			Education
			B.Tech, Computer Science  2017 - 2021
			Example Institute of Technology
			8.5 CGPA
			Skills
			Languages: Python, JavaScript, Go
			Frameworks: FastAPI, React, Spring Boot
			Tools: Docker, Kubernetes
			Projects
			Resume Maker AI Agent
			• AI-powered resume optimizer
			Technologies: Python, FastAPI
			Certifications
			AWS Certified Developer - Associate - Amazon Web Services
			""";

	@Test
	void parsesSectionsFromResumeText() {
		ResumeRequest r = new ResumeParser().parseText(SAMPLE);

		assertThat(r.profile().fullName()).isEqualTo("Suraj Singh Karki");
		assertThat(r.profile().jobTitle()).isEqualTo("Senior Software Engineer");
		assertThat(r.profile().email()).isEqualTo("suraj.karki@coredge.io");
		assertThat(r.profile().phone()).isEqualTo("+91-9800000000");
		assertThat(r.profile().linkedin()).isEqualTo("linkedin.com/in/surajsingh");
		assertThat(r.profile().summary()).startsWith("Results-driven");

		assertThat(r.experience()).hasSize(2);
		assertThat(r.experience().get(0).jobTitle()).isEqualTo("Senior Backend Engineer");
		assertThat(r.experience().get(0).company()).isEqualTo("Coredge");
		assertThat(r.experience().get(0).current()).isTrue();
		assertThat(r.experience().get(0).achievements()).contains("• Mentored 2 junior engineers");
		assertThat(r.experience().get(1).jobTitle()).isEqualTo("Software Engineer");
		assertThat(r.experience().get(1).company()).isEqualTo("Previous Company Pvt. Ltd.");

		assertThat(r.education()).hasSize(1);
		assertThat(r.education().get(0).degree()).isEqualTo("B.Tech, Computer Science");
		assertThat(r.education().get(0).university()).isEqualTo("Example Institute of Technology");
		assertThat(r.education().get(0).grade()).isEqualTo("8.5 CGPA");

		assertThat(r.skills().languages()).containsExactly("Python", "JavaScript", "Go");
		assertThat(r.skills().frameworks()).containsExactly("FastAPI", "React", "Spring Boot");
		assertThat(r.skills().tools()).containsExactly("Docker", "Kubernetes");

		assertThat(r.projects()).hasSize(1);
		assertThat(r.projects().get(0).name()).isEqualTo("Resume Maker AI Agent");
		assertThat(r.projects().get(0).technologies()).isEqualTo("Python, FastAPI");

		assertThat(r.certifications()).hasSize(1);
		assertThat(r.certifications().get(0).issuer()).isEqualTo("Amazon Web Services");
	}
}
