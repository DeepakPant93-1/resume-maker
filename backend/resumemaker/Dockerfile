# Build stage: compile the Spring Boot jar with the Maven wrapper
FROM eclipse-temurin:25-jdk AS build

WORKDIR /workspace

# Resolve dependencies first so they are cached until pom.xml changes
COPY .mvn .mvn
COPY mvnw pom.xml ./
RUN chmod +x mvnw && ./mvnw -B -q dependency:go-offline

COPY src src
RUN ./mvnw -B -q package -DskipTests

# Runtime stage
FROM eclipse-temurin:25-jre

WORKDIR /app

# curl is used by the health check. pdflatex (texlive-latex-base) compiles the resume templates to PDF;
# cm-super-minimal and texlive-fonts-recommended give it vector fonts, so no blurry bitmap glyphs end up in the PDF;
# lmodern is the Latin Modern font the modern template uses.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
        texlive-latex-base texlive-fonts-recommended cm-super-minimal lmodern \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /workspace/target/resumemaker-*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fs http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
