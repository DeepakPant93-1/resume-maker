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

		assertThat(r.getProfile().getFullName()).isEqualTo("Suraj Singh Karki");
		assertThat(r.getProfile().getJobTitle()).isEqualTo("Senior Software Engineer");
		assertThat(r.getProfile().getEmail()).isEqualTo("suraj.karki@coredge.io");
		assertThat(r.getProfile().getPhone()).isEqualTo("+91-9800000000");
		assertThat(r.getProfile().getLinkedin()).isEqualTo("linkedin.com/in/surajsingh");
		assertThat(r.getProfile().getSummary()).startsWith("Results-driven");

		assertThat(r.getExperience()).hasSize(2);
		assertThat(r.getExperience().get(0).getJobTitle()).isEqualTo("Senior Backend Engineer");
		assertThat(r.getExperience().get(0).getCompany()).isEqualTo("Coredge");
		assertThat(r.getExperience().get(0).isCurrent()).isTrue();
		assertThat(r.getExperience().get(0).getAchievements()).contains("• Mentored 2 junior engineers");
		assertThat(r.getExperience().get(1).getJobTitle()).isEqualTo("Software Engineer");
		assertThat(r.getExperience().get(1).getCompany()).isEqualTo("Previous Company Pvt. Ltd.");

		assertThat(r.getEducation()).hasSize(1);
		assertThat(r.getEducation().get(0).getDegree()).isEqualTo("B.Tech, Computer Science");
		assertThat(r.getEducation().get(0).getUniversity()).isEqualTo("Example Institute of Technology");
		assertThat(r.getEducation().get(0).getGrade()).isEqualTo("8.5 CGPA");

		assertThat(r.getSkills().getLanguages()).containsExactly("Python", "JavaScript", "Go");
		assertThat(r.getSkills().getFrameworks()).containsExactly("FastAPI", "React", "Spring Boot");
		assertThat(r.getSkills().getTools()).containsExactly("Docker", "Kubernetes");

		assertThat(r.getProjects()).hasSize(1);
		assertThat(r.getProjects().get(0).getName()).isEqualTo("Resume Maker AI Agent");
		assertThat(r.getProjects().get(0).getTechnologies()).isEqualTo("Python, FastAPI");

		assertThat(r.getCertifications()).hasSize(1);
		assertThat(r.getCertifications().get(0).getIssuer()).isEqualTo("Amazon Web Services");
	}
}
