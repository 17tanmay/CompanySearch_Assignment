# Job Search Engine

A comprehensive job search engine built with Elasticsearch, FastAPI, and React, featuring advanced search capabilities, fuzzy matching, and a tagging system.

## Architecture

- **Backend**: FastAPI with Elasticsearch integration
- **Frontend**: React with modern UI components
- **Search Engine**: Elasticsearch with advanced search features
- **Data Pipeline**: Python script for CSV ingestion
- **Containerization**: Docker Compose for easy deployment

## Features

- **Advanced Search**: Fuzzy search, ngrams, and relevance scoring
- **Filtering**: Industry, company size, location, founding year
- **Tagging System**: Personal and shared tags for company organization
- **Real-time Search**: Fast search with instant results
- **Responsive UI**: Modern, mobile-friendly interface

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-search-engine
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Ingest sample data**
   ```bash
   docker-compose exec data-pipeline python ingest_data.py
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Elasticsearch: http://localhost:9200

## Data Pipeline

The data pipeline processes CSV files and ingests them into Elasticsearch with proper mapping and indexing.

### Sample Data Format
```csv
name,domain,year founded,industry,size range,locality,country,linkedin url,current employee estimate,total employee estimate
ibm,ibm.com,1911.0,information technology and services,10001+,"new york, new york, united states",united states,linkedin.com/company/ibm,274047,716906
```

## API Endpoints

- `GET /search` - Search companies with filters
- `POST /companies` - Create/update company
- `GET /companies/{id}` - Get company details
- `POST /tags` - Create tag
- `GET /tags` - List all tags
- `POST /companies/{id}/tags` - Add tag to company

## Search Features

- **Fuzzy Search**: Handles typos and variations
- **Ngrams**: Partial word matching
- **Faceted Search**: Filter by multiple criteria
- **Relevance Scoring**: Intelligent result ranking
- **Auto-complete**: Search suggestions

## Tagging System

Users can create and manage tags for companies:
- **Personal Tags**: Private to each user
- **Shared Tags**: Visible to all users
- **Tag Management**: Create, edit, and delete tags
- **Bulk Operations**: Apply tags to multiple companies

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Data Pipeline
```bash
cd data-pipeline
pip install -r requirements.txt
python ingest_data.py
```

