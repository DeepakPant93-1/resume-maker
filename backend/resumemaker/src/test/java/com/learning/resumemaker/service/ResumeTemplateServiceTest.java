package com.learning.resumemaker.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.learning.resumemaker.document.ResumeDocument;
import com.learning.resumemaker.exception.TemplateNotFoundException;
import com.learning.resumemaker.model.ResumeTemplate;

class ResumeTemplateServiceTest {

	private final ResumeTemplateService service = new ResumeTemplateService();

	private static ResumeDocument resume() {
		return ResumeDocument.builder()
				.profile(ResumeDocument.Profile.builder().fullName("Jane Doe").jobTitle("R&D Engineer")
						.email("jane@example.com").linkedin("linkedin.com/in/jane").summary("Cut costs by 20% at $0 cost")
						.build())
				.experience(List.of(ResumeDocument.Experience.builder().jobTitle("Engineer").company("Acme_Co")
						.startDate("Jan 2024").current(true).achievements("- Shipped feature #1\n\n• Fixed {bugs}").build()))
				.skills(ResumeDocument.Skills.builder().languages(List.of("Java", "C++")).build())
				.certifications(List.of(ResumeDocument.Certification.builder().name("AWS").issuer("Amazon").build()))
				.build();
	}

	@Test
	void listsOnlyTemplatesWithPlaceholders() {
		// resume-classic.tex and resume-v1.tex are filled samples without placeholders
		assertThat(service.listTemplates()).containsExactly(new ResumeTemplate("classic", "Classic"),
				new ResumeTemplate("modern", "Modern"));
	}

	@Test
	void rendersTheModernTemplate() {
		String latex = service.renderTemplate("modern", resume());

		assertThat(latex).startsWith("\\documentclass").contains("\\usepackage{lmodern}", "\\end{document}")
				.contains("{\\LARGE\\bfseries {Jane Doe}}")
				.contains("\\href{mailto:jane@example.com}{jane@example.com}")
				.contains("\\href{https://linkedin.com/in/jane}{LinkedIn}")
				.contains("{\\bfseries {Engineer}} \\hfill {Jan 2024 -- Present}")
				.contains("{\\itshape {Acme\\_Co}}")
				.contains("\\item {Shipped feature \\#1}", "\\item {Fixed \\{bugs\\}}")
				.contains("{\\bfseries {Programming}:} {Java, C++}")
				.doesNotContain("[=", "enumitem");
	}

	@Test
	void rendersTheResumeWithLatexSpecialCharactersEscaped() {
		String latex = service.renderTemplate("classic", resume());

		assertThat(latex).contains("\\documentclass", "\\end{document}")
				.contains("{\\Huge\\bfseries {Jane Doe}}")
				.contains("{R\\&D Engineer}")
				.contains("Cut costs by 20\\% at \\$0 cost")
				.contains("\\href{https://linkedin.com/in/jane}")
				.contains("Jan 2024 -- Present")
				.contains("{Acme\\_Co}")
				.contains("\\item {Shipped feature \\#1}", "\\item {Fixed \\{bugs\\}}")
				.contains("{\\bfseries {Programming Languages}}: {Java, C++}")
				.doesNotContain("[=");
	}

	@Test
	void leavesOutTheTemplatesCommentLines() {
		String latex = service.renderTemplate("classic", resume());

		assertThat(latex).startsWith("\\documentclass").doesNotContain("FreeMarker", "\n%", "\n\n\n")
				.contains("}%\n"); // a comment after code (certifications) is kept
	}

	@Test
	void rendersAnEmptyResumeWithoutSections() {
		for (ResumeTemplate template : service.listTemplates()) {
			String latex = service.renderTemplate(template.id(), new ResumeDocument());

			assertThat(latex).as(template.id()).contains("\\begin{document}", "\\end{document}")
					.doesNotContain("Experience", "Education", "Technical Skills");
		}
	}

	@Test
	void rejectsAnUnknownTemplate() {
		assertThatThrownBy(() -> service.renderTemplate("../application.yaml", resume()))
				.isInstanceOf(TemplateNotFoundException.class);
	}
}
