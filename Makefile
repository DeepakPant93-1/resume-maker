.PHONY: build run stop help docker-build docker-run docker-stop

help:
	@echo "Available commands:"
	@echo "  make build              - Install dependencies for the frontend"
	@echo "  make run                - Start the Streamlit frontend application"
	@echo "  make stop               - Stop the Streamlit application"
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
