#!/bin/bash

echo "🚀 Starting Job Search Engine..."

# Create data directory if it doesn't exist
mkdir -p data

# Start all services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for Elasticsearch to be ready
echo "⏳ Waiting for Elasticsearch to be ready..."
until curl -s http://localhost:9200 > /dev/null; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

echo "✅ Elasticsearch is ready!"

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
until curl -s http://localhost:8000/health > /dev/null; do
  echo "Waiting for API..."
  sleep 5
done

echo "✅ API is ready!"

# Ingest sample data
echo "📊 Ingesting sample data..."
docker-compose exec data-pipeline python ingest_data.py

echo "🎉 Job Search Engine is ready!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   Elasticsearch: http://localhost:9200"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop the services, run: docker-compose down"

