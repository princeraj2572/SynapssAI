#!/bin/bash
# Run after: docker compose up -d ollama
echo "Pulling Llama 3.1 8B model (this takes a few minutes)..."
docker exec lifeOS_ollama ollama pull llama3.1:8b
echo "Done. Test with: curl http://localhost:11434/api/tags"
