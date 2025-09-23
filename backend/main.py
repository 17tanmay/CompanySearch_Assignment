from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import json

app = FastAPI(title="Job Search API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch client
es_client = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")])

# Pydantic models
class Company(BaseModel):
    id: Optional[str] = None
    name: str
    domain: str
    year_founded: Optional[float] = None
    industry: str
    size_range: str
    locality: str
    country: str
    linkedin_url: str
    current_employee_estimate: int
    total_employee_estimate: int
    tags: List[str] = []

class Tag(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_shared: bool = False
    created_by: Optional[str] = None

class SearchRequest(BaseModel):
    query: Optional[str] = None
    industry: Optional[List[str]] = None
    size_range: Optional[List[str]] = None
    country: Optional[List[str]] = None
    locality: Optional[List[str]] = None
    year_founded_from: Optional[int] = None
    year_founded_to: Optional[int] = None
    tags: Optional[List[str]] = None
    page: int = 1
    size: int = 20
    sort_by: str = "relevance"

class SearchResponse(BaseModel):
    companies: List[Company]
    total: int
    page: int
    size: int
    total_pages: int

# Initialize Elasticsearch index
@app.on_event("startup")
async def create_index():
    """Create Elasticsearch index with proper mapping"""
    import time
    
    # Wait for Elasticsearch to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if es_client.ping():
                break
        except Exception:
            pass
        
        retry_count += 1
        time.sleep(2)
    
    if retry_count >= max_retries:
        print("Warning: Could not connect to Elasticsearch after 60 seconds")
        return
    
    index_name = "companies"
    
    try:
        if not es_client.indices.exists(index=index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "name": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"},
                                "suggest": {
                                    "type": "completion",
                                    "analyzer": "standard"
                                }
                            }
                        },
                        "domain": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "year_founded": {"type": "float"},
                        "industry": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "size_range": {"type": "keyword"},
                    "size_category": {"type": "keyword"},
                        "locality": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "country": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "linkedin_url": {"type": "keyword"},
                        "current_employee_estimate": {"type": "integer"},
                        "total_employee_estimate": {"type": "integer"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index.max_ngram_diff": 10,
                    "analysis": {
                        "analyzer": {
                            "ngram_analyzer": {
                                "tokenizer": "ngram_tokenizer"
                            }
                        },
                        "tokenizer": {
                            "ngram_tokenizer": {
                                "type": "ngram",
                                "min_gram": 2,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"]
                            }
                        }
                    }
                }
            }
        
            es_client.indices.create(index=index_name, body=mapping)
            print(f"Created index: {index_name}")
    except Exception as e:
        print(f"Error creating index: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Search companies
@app.post("/search", response_model=SearchResponse)
async def search_companies(search_request: SearchRequest):
    """Search companies with advanced filters and fuzzy matching"""
    
    query_body = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "from": (search_request.page - 1) * search_request.size,
        "size": search_request.size
    }
    
    # Text search with fuzzy matching
    if search_request.query:
        query_body["query"]["bool"]["must"].append({
            "multi_match": {
                "query": search_request.query,
                "fields": [
                    "name^3",
                    "domain^2",
                    "industry^2",
                    "locality^2",
                    "country^2"
                ],
                "fuzziness": "AUTO",
                "type": "best_fields"
            }
        })
    
    # Filters
    if search_request.industry:
        query_body["query"]["bool"]["filter"].append({
            "terms": {"industry.keyword": search_request.industry}
        })
    
    if search_request.size_range:
        # Convert size categories to employee count ranges
        size_filters = []
        for size_cat in search_request.size_range:
            if size_cat == "Large (10001+)":
                size_filters.append({
                    "range": {"current_employee_estimate": {"gte": 10001}}
                })
            elif size_cat == "Medium (1000-10000)":
                size_filters.append({
                    "range": {"current_employee_estimate": {"gte": 1000, "lte": 10000}}
                })
            elif size_cat == "Small (<1000)":
                size_filters.append({
                    "range": {"current_employee_estimate": {"lt": 1000}}
                })
        
        if size_filters:
            query_body["query"]["bool"]["filter"].append({
                "bool": {"should": size_filters}
            })
    
    if search_request.country:
        query_body["query"]["bool"]["filter"].append({
            "terms": {"country.keyword": search_request.country}
        })
    
    if search_request.locality:
        query_body["query"]["bool"]["filter"].append({
            "terms": {"locality.keyword": search_request.locality}
        })
    
    if search_request.year_founded_from or search_request.year_founded_to:
        year_range = {}
        if search_request.year_founded_from:
            year_range["gte"] = search_request.year_founded_from
        if search_request.year_founded_to:
            year_range["lte"] = search_request.year_founded_to
        query_body["query"]["bool"]["filter"].append({
            "range": {"year_founded": year_range}
        })
    
    if search_request.tags:
        query_body["query"]["bool"]["filter"].append({
            "terms": {"tags": search_request.tags}
        })
    
    # Sorting
    if search_request.sort_by == "name":
        query_body["sort"] = [{"name.keyword": {"order": "asc"}}]
    elif search_request.sort_by == "size":
        query_body["sort"] = [{"current_employee_estimate": {"order": "desc"}}]
    else:  # relevance
        query_body["sort"] = ["_score"]
    
    try:
        response = es_client.search(index="companies", body=query_body)
        
        companies = []
        for hit in response["hits"]["hits"]:
            company_data = hit["_source"]
            company_data["id"] = hit["_id"]
            companies.append(Company(**company_data))
        
        total = response["hits"]["total"]["value"]
        total_pages = (total + search_request.size - 1) // search_request.size
        
        return SearchResponse(
            companies=companies,
            total=total,
            page=search_request.page,
            size=search_request.size,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Get company by ID
@app.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """Get a specific company by ID"""
    try:
        response = es_client.get(index="companies", id=company_id)
        company_data = response["_source"]
        company_data["id"] = response["_id"]
        return Company(**company_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Company not found")

# Create or update company
@app.post("/companies", response_model=Company)
async def create_company(company: Company):
    """Create or update a company"""
    try:
        company_data = company.dict(exclude={"id"})
        company_data["created_at"] = datetime.now().isoformat()
        company_data["updated_at"] = datetime.now().isoformat()
        
        if company.id:
            # Update existing company
            es_client.index(index="companies", id=company.id, body=company_data)
            company_id = company.id
        else:
            # Create new company
            response = es_client.index(index="companies", body=company_data)
            company_id = response["_id"]
        
        company_data["id"] = company_id
        return Company(**company_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save company: {str(e)}")

# Get all tags
@app.get("/tags", response_model=List[Tag])
async def get_tags():
    """Get all available tags"""
    try:
        response = es_client.search(
            index="tags",
            body={"query": {"match_all": {}}}
        )
        
        tags = []
        for hit in response["hits"]["hits"]:
            tag_data = hit["_source"]
            tag_data["id"] = hit["_id"]
            tags.append(Tag(**tag_data))
        
        return tags
    
    except Exception as e:
        return []  # Return empty list if tags index doesn't exist

# Create tag
@app.post("/tags", response_model=Tag)
async def create_tag(tag: Tag):
    """Create a new tag"""
    try:
        tag_data = tag.dict(exclude={"id"})
        tag_data["created_at"] = datetime.now().isoformat()
        
        response = es_client.index(index="tags", body=tag_data)
        tag_id = response["_id"]
        
        tag_data["id"] = tag_id
        return Tag(**tag_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tag: {str(e)}")

# Add tag to company
@app.post("/companies/{company_id}/tags")
async def add_tag_to_company(company_id: str, tag_name: str):
    """Add a tag to a company"""
    try:
        # Get current company
        response = es_client.get(index="companies", id=company_id)
        company_data = response["_source"]
        
        # Add tag if not already present
        if tag_name not in company_data.get("tags", []):
            company_data["tags"] = company_data.get("tags", []) + [tag_name]
            company_data["updated_at"] = datetime.now().isoformat()
            
            es_client.index(index="companies", id=company_id, body=company_data)
        
        return {"message": "Tag added successfully", "tags": company_data["tags"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add tag: {str(e)}")

# Remove tag from company
@app.delete("/companies/{company_id}/tags")
async def remove_tag_from_company(company_id: str, tag_name: str):
    """Remove a tag from a company"""
    try:
        # Get current company
        response = es_client.get(index="companies", id=company_id)
        company_data = response["_source"]
        
        # Remove tag if present
        current_tags = company_data.get("tags", [])
        if tag_name in current_tags:
            company_data["tags"] = [tag for tag in current_tags if tag != tag_name]
            company_data["updated_at"] = datetime.now().isoformat()
            
            es_client.index(index="companies", id=company_id, body=company_data)
        
        return {"message": "Tag removed successfully", "tags": company_data["tags"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove tag: {str(e)}")

# Get company tags
@app.get("/companies/{company_id}/tags")
async def get_company_tags(company_id: str):
    """Get all tags for a specific company"""
    try:
        response = es_client.get(index="companies", id=company_id)
        company_data = response["_source"]
        return {"tags": company_data.get("tags", [])}
    
    except Exception as e:
        raise HTTPException(status_code=404, detail="Company not found")

# Get search suggestions
@app.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    """Get search suggestions for autocomplete"""
    try:
        response = es_client.search(
            index="companies",
            body={
                "suggest": {
                    "company_suggest": {
                        "prefix": q,
                        "completion": {
                            "field": "name.suggest",
                            "size": 10
                        }
                    }
                }
            }
        )
        
        suggestions = []
        for option in response["suggest"]["company_suggest"][0]["options"]:
            suggestions.append(option["text"])
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        return {"suggestions": []}

# Get city suggestions
@app.get("/suggest/cities")
async def get_city_suggestions(q: str = Query(..., min_length=1)):
    """Get city suggestions for autocomplete"""
    try:
        response = es_client.search(
            index="companies",
            body={
                "size": 0,
                "aggs": {
                    "cities": {
                        "terms": {
                            "field": "locality.keyword",
                            "include": f".*{q}.*",
                            "size": 5
                        }
                    }
                }
            }
        )
        
        suggestions = []
        for bucket in response["aggregations"]["cities"]["buckets"]:
            suggestions.append(bucket["key"])
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        return {"suggestions": []}

# Get filter options
@app.get("/filters")
async def get_filter_options():
    """Get available filter options"""
    try:
        # Get unique values for each filter field
        response = es_client.search(
            index="companies",
            body={
                "size": 0,
                "aggs": {
                    "industries": {
                        "terms": {"field": "industry.keyword", "size": 100}
                    },
                    "size_ranges": {
                        "terms": {"field": "size_category", "size": 100}
                    },
                    "countries": {
                        "terms": {"field": "country.keyword", "size": 100}
                    },
                    "localities": {
                        "terms": {"field": "locality.keyword", "size": 100}
                    }
                }
            }
        )
        
        return {
            "industries": [bucket["key"] for bucket in response["aggregations"]["industries"]["buckets"]],
            "size_ranges": [bucket["key"] for bucket in response["aggregations"]["size_ranges"]["buckets"]],
            "countries": [bucket["key"] for bucket in response["aggregations"]["countries"]["buckets"]],
            "localities": [bucket["key"] for bucket in response["aggregations"]["localities"]["buckets"]]
        }
    
    except Exception as e:
        return {
            "industries": [],
            "size_ranges": [],
            "countries": [],
            "localities": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

