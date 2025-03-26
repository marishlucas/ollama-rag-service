# Ollama RAG Service

A complete Retrieval-Augmented Generation (RAG) service using Ollama, ChromaDB, and Streamlit, optimized for Apple Silicon (M1/M2/M3/M4) machines.

## Features

- 🤖 **Ollama Integration**: Run LLMs locally with GPU acceleration
- 🔍 **Vector Database**: ChromaDB for efficient document storage and retrieval
- 📊 **Web Interface**: Streamlit for document uploads and question answering
- 🚀 **Docker-based**: Fully containerized for easy deployment and management
- 🔧 **Makefile Commands**: Simple commands for managing the entire system
- 📱 **Apple Silicon Optimized**: Configurations for M-series chip performance

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone this repository)
- Make utility

### Setup and Run

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/ollama-rag-service.git
   cd ollama-rag-service
   ```

2. Run the setup:

   ```bash
   make setup
   ```

3. Start the service:

   ```bash
   make start
   ```

4. Pull required models:

   ```bash
   make pull-models
   ```

5. Access the RAG application:
   - Open your browser and go to: http://localhost:8501

### Using the RAG System

1. Upload PDF documents using the file uploader in the web interface
2. Wait for document processing to complete
3. Ask questions about the content of your documents
4. The system will retrieve relevant context and provide answers based on your documents

## Configuration

You can customize the service by editing the `.env` file:

- Change port mappings
- Configure default models
- Adjust chunk sizes for document processing

## Available Commands

Run `make help` to see all available commands:

- `make setup` - Initial setup
- `make start` - Start all containers
- `make stop` - Stop all containers
- `make restart` - Restart all containers
- `make status` - Show container status
- `make logs` - Show container logs
- `make pull-models` - Pull Ollama models
- `make build` - Build custom models
- `make clean` - Remove all containers and volumes
- `make rebuild` - Rebuild the rag-app container

## Custom Models

To create custom Ollama models:

1. Add your Modelfile to the `models/` directory with the naming convention `Modelfile.your-model-name`
2. Run `make build` to build all custom models

## Directory Structure

```
ollama-rag-service/
├── Makefile
├── docker-compose.yml
├── .env
├── README.md
├── models/
│   └── Modelfile.llama3-optimized
├── rag-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── utils/
│       ├── __init__.py
│       ├── document_processor.py
│       └── rag_chain.py
└── scripts/
    ├── setup.sh
    └── pull_models.sh
```

## Performance Optimization

The service is configured to take advantage of Apple Silicon GPUs. You can adjust these settings in the model configurations and docker-compose.yml file.

## Troubleshooting

If you encounter issues:

1. Check the logs with `make logs`
2. Ensure your models are properly pulled with `make pull-models`
3. Restart the service with `make restart`

## License

MIT
