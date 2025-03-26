#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Ollama RAG Service...${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
# Ports
OLLAMA_PORT=11434
CHROMA_PORT=8000
APP_PORT=8501

# Models
DEFAULT_MODEL=llama3
EMBEDDING_MODEL=nomic-embed-text

# Document processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=5
EOL
    echo -e "${GREEN}.env file created.${NC}"
fi

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/chroma_db
mkdir -p data/uploads
mkdir -p models

# Create a sample Modelfile if none exist
if [ ! -f models/Modelfile.* ]; then
    echo -e "${YELLOW}Creating sample Modelfile...${NC}"
    cat > models/Modelfile.llama3-optimized << EOL
FROM llama3

# System prompt to optimize for RAG
SYSTEM """
You are a helpful, accurate, and concise AI assistant. When answering questions:
1. Only answer based on the provided context.
2. If you don't know the answer or can't find it in the context, say "I don't have enough information to answer this question."
3. Do not make up information or use prior knowledge outside of the provided context.
4. When quoting from the context, be accurate and provide the source.
5. Format your responses in a clear, organized way.
"""

# Parameter settings optimized for RAG
PARAMETER stop "Human:"
PARAMETER stop "Assistant:"
PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER top_k 50
EOL
    echo -e "${GREEN}Sample Modelfile created.${NC}"
fi

echo -e "${GREEN}Setup complete! Next steps:${NC}"
echo -e "1. Run ${YELLOW}make start${NC} to start the services"
echo -e "2. Run ${YELLOW}make pull-models${NC} to pull the required models"
echo -e "3. Access the RAG app at ${YELLOW}http://localhost:8501${NC}"