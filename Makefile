.PHONY: build run stop help run-agent stop-agent run-backend stop-backend restart-backend docker-build docker-run docker-stop restart-agent

help:
	@echo "Available commands:"
	@echo "  make build              - Install dependencies for the frontend"
	@echo "  make run                - Start the Streamlit frontend application"
	@echo "  make stop               - Stop the Streamlit application"
	@echo "  make run-agent          - Start the Python agent service on port 8000"
	@echo "  make stop-agent         - Stop the agent service"
	@echo "  make restart-agent      - Stop, then start the agent service"
	@echo "  make run-backend        - Start the Spring Boot API on port 8080 (starts MongoDB via Docker)"
	@echo "  make stop-backend       - Stop whatever is listening on port 8080"
	@echo "  make restart-backend    - Stop, then start the Spring Boot API"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build       - Build the Docker image for the frontend"
	@echo "  make docker-run         - Run the frontend application in Docker"
	@echo "  make docker-stop        - Stop the Docker container"

build:
	@echo "Building frontend..."
	pip install -r frontend/requirements.txt

run:
	@echo "Starting Streamlit app..."
	streamlit run frontend/app.py

stop:
	@echo "Stopping Streamlit application..."
	pkill -f "streamlit run" || echo "No Streamlit process found"

docker-build:
	@echo "Building Docker image for frontend application..."
	docker build -t resume-maker-frontend:latest -f frontend/Dockerfile frontend/

docker-run:
	@echo "Running frontend application in Docker container..."
	docker run -p 8501:8501 --name resume-maker-frontend resume-maker-frontend:latest

docker-stop:
	@echo "Stopping frontend Docker container..."
	docker stop resume-maker-frontend && docker rm resume-maker-frontend || echo "No running frontend container found"

run-agent:
	@echo "Starting agent service on :8000..."
	cd backend/agents && .venv/bin/uvicorn app.main:app --reload --port 8000

# With --reload, uvicorn runs the server in a spawned child whose command line does not mention uvicorn and
# which outlives a killed reloader, so killing by name is not enough: free port 8000 itself as well.
stop-agent:
	@echo "Stopping agent service..."
	@pkill -f "uvicorn app.main:app" || true
	@sleep 1
	@pids=$$(lsof -tiTCP:8000 -sTCP:LISTEN); \
	if [ -z "$$pids" ]; then echo "Port 8000 is free"; exit 0; fi; \
	ps -o pid=,command= -p $$pids | cut -c1-120; \
	kill $$pids; sleep 2; \
	pids=$$(lsof -tiTCP:8000 -sTCP:LISTEN); \
	if [ -n "$$pids" ]; then kill -9 $$pids && echo "Force-killed process still on :8000"; fi; \
	echo "Port 8000 is free"

restart-agent: stop-agent run-agent

# Run from backend/resumemaker: Spring's Docker Compose support looks for compose.yaml in the working directory.
run-backend:
	@echo "Starting Spring Boot API on :8080..."
	cd backend/resumemaker && ./mvnw spring-boot:run

# Frees port 8080 ("Web server failed to start. Port 8080 was already in use"). Kills by port because the
# leftover is often an old run of this app, and it can ignore a normal kill, so escalate to kill -9.
stop-backend:
	@echo "Stopping whatever is listening on :8080..."
	@pids=$$(lsof -tiTCP:8080 -sTCP:LISTEN); \
	if [ -z "$$pids" ]; then echo "Nothing is listening on :8080"; exit 0; fi; \
	ps -o pid=,command= -p $$pids | cut -c1-120; \
	kill $$pids; sleep 3; \
	pids=$$(lsof -tiTCP:8080 -sTCP:LISTEN); \
	if [ -n "$$pids" ]; then kill -9 $$pids && echo "Force-killed process still on :8080"; fi; \
	echo "Port 8080 is free"

restart-backend: stop-backend run-backend
