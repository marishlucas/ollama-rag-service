.PHONY: help setup start stop restart status logs clean pull-models build rebuild

# Colors for terminal output
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

help:
	@echo "$(GREEN)Ollama RAG Service Management$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo "  $(GREEN)make setup$(NC)         - Initial setup (create directories, etc.)"
	@echo "  $(GREEN)make start$(NC)         - Start all containers"
	@echo "  $(GREEN)make stop$(NC)          - Stop all containers"
	@echo "  $(GREEN)make restart$(NC)       - Restart all containers"
	@echo "  $(GREEN)make status$(NC)        - Show container status"
	@echo "  $(GREEN)make logs$(NC)          - Show container logs"
	@echo "  $(GREEN)make pull-models$(NC)   - Pull Ollama models"
	@echo "  $(GREEN)make build$(NC)         - Build custom models"
	@echo "  $(GREEN)make clean$(NC)         - Remove all containers and volumes"
	@echo "  $(GREEN)make rebuild$(NC)       - Rebuild the rag-app container"

setup:
	@echo "$(GREEN)Setting up Ollama RAG service...$(NC)"
	@mkdir -p data/chroma_db
	@mkdir -p data/uploads
	@chmod +x scripts/setup.sh
	@chmod +x scripts/pull_models.sh
	@./scripts/setup.sh
	@echo "$(GREEN)Setup complete.$(NC)"

start:
	@echo "$(GREEN)Starting Ollama RAG service...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)Service started.$(NC)"
	@echo "$(YELLOW)RAG App is available at: http://localhost:8501$(NC)"
	@echo "$(YELLOW)Ollama API is available at: http://localhost:11434$(NC)"

stop:
	@echo "$(YELLOW)Stopping Ollama RAG service...$(NC)"
	@docker-compose down
	@echo "$(GREEN)Service stopped.$(NC)"

restart: stop start

status:
	@echo "$(GREEN)Container status:$(NC)"
	@docker-compose ps

logs:
	@echo "$(GREEN)Container logs:$(NC)"
	@docker-compose logs -f

clean:
	@echo "$(RED)Warning: This will remove all containers and volumes.$(NC)"
	@read -p "Are you sure you want to continue? (y/n) " confirm; \
	if [ "$$confirm" = "y" ]; then \
		echo "$(YELLOW)Removing containers and volumes...$(NC)"; \
		docker-compose down -v; \
		echo "$(GREEN)Cleaned up successfully.$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

pull-models:
	@echo "$(GREEN)Pulling Ollama models...$(NC)"
	@./scripts/pull_models.sh
	@echo "$(GREEN)Models pulled successfully.$(NC)"

build:
	@echo "$(GREEN)Building custom Ollama models...$(NC)"
	@for file in models/Modelfile.*; do \
		model_name=$$(basename "$$file" | sed 's/Modelfile\.//'); \
		echo "$(YELLOW)Building model: $$model_name$(NC)"; \
		docker exec -it ollama ollama create "$$model_name" -f /models/$$(basename "$$file"); \
	done
	@echo "$(GREEN)Models built successfully.$(NC)"

rebuild:
	@echo "$(YELLOW)Rebuilding rag-app container...$(NC)"
	@docker-compose up -d --no-deps --build rag-app
	@echo "$(GREEN)Rebuild complete.$(NC)"
