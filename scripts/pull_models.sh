#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pulling required Ollama models...${NC}"

# Wait until ollama container is ready
echo -e "${YELLOW}Waiting for Ollama service to be ready...${NC}"
while ! curl -s --fail http://localhost:11434/api/version &>/dev/null; do
  echo -e "${YELLOW}Ollama not ready, waiting...${NC}"
  sleep 5
done

echo -e "${GREEN}Ollama service is ready.${NC}"

# Pull the models
echo -e "${YELLOW}Pulling LLM model: llama3${NC}"
docker exec ollama ollama pull llama3

echo -e "${YELLOW}Pulling embedding model: nomic-embed-text${NC}"
docker exec ollama ollama pull nomic-embed-text

# Pull additional models (optional)
pull_additional() {
  read -p "Do you want to pull additional models? (y/n) " choice
  case "$choice" in 
    y|Y ) 
      echo -e "${YELLOW}Pulling additional models...${NC}"
      docker exec ollama ollama pull llama3:8b
      docker exec ollama ollama pull mistral
      echo -e "${GREEN}Additional models pulled.${NC}"
      ;;
    n|N ) 
      echo -e "${GREEN}Skipping additional models.${NC}"
      ;;
    * ) 
      echo -e "${RED}Invalid input. Please enter 'y' or 'n'.${NC}"
      pull_additional
      ;;
  esac
}

pull_additional

echo -e "${GREEN}Model pulling complete. Available models:${NC}"
docker exec ollama ollama list