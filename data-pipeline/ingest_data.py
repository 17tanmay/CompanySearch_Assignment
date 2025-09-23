#!/usr/bin/env python3
"""
Data pipeline to ingest CSV data into Elasticsearch
"""

import os
import pandas as pd
from elasticsearch import Elasticsearch
from datetime import datetime
import json
import sys

def connect_to_elasticsearch():
    """Connect to Elasticsearch"""
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    es_client = Elasticsearch([es_url])
    
    # Test connection
    if not es_client.ping():
        raise Exception(f"Could not connect to Elasticsearch at {es_url}")
    
    print(f"Connected to Elasticsearch at {es_url}")
    return es_client

def create_index_mapping(es_client):
    """Create the companies index with proper mapping"""
    index_name = "companies"
    
    # Delete index if it exists
    if es_client.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}")
        es_client.indices.delete(index=index_name)
    
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

def create_sample_data():
    """Create sample data if no CSV file is provided"""
    sample_data = [
        {
            "name": "IBM",
            "domain": "ibm.com",
            "year_founded": 1911.0,
            "industry": "information technology and services",
            "size_range": "10001+",
            "locality": "new york, new york, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/ibm",
            "current_employee_estimate": 274047,
            "total_employee_estimate": 716906
        },
        {
            "name": "Tata Consultancy Services",
            "domain": "tcs.com",
            "year_founded": 1968.0,
            "industry": "information technology and services",
            "size_range": "10001+",
            "locality": "bombay, maharashtra, india",
            "country": "india",
            "linkedin_url": "linkedin.com/company/tata-consultancy-services",
            "current_employee_estimate": 190771,
            "total_employee_estimate": 341369
        },
        {
            "name": "Accenture",
            "domain": "accenture.com",
            "year_founded": 1989.0,
            "industry": "information technology and services",
            "size_range": "10001+",
            "locality": "dublin, dublin, ireland",
            "country": "ireland",
            "linkedin_url": "linkedin.com/company/accenture",
            "current_employee_estimate": 190689,
            "total_employee_estimate": 455768
        },
        {
            "name": "Microsoft",
            "domain": "microsoft.com",
            "year_founded": 1975.0,
            "industry": "computer software",
            "size_range": "10001+",
            "locality": "redmond, washington, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/microsoft",
            "current_employee_estimate": 221000,
            "total_employee_estimate": 221000
        },
        {
            "name": "Google",
            "domain": "google.com",
            "year_founded": 1998.0,
            "industry": "internet",
            "size_range": "10001+",
            "locality": "mountain view, california, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/google",
            "current_employee_estimate": 190000,
            "total_employee_estimate": 190000
        },
        {
            "name": "Amazon",
            "domain": "amazon.com",
            "year_founded": 1994.0,
            "industry": "internet",
            "size_range": "10001+",
            "locality": "seattle, washington, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/amazon",
            "current_employee_estimate": 1500000,
            "total_employee_estimate": 1500000
        },
        {
            "name": "Apple",
            "domain": "apple.com",
            "year_founded": 1976.0,
            "industry": "consumer electronics",
            "size_range": "10001+",
            "locality": "cupertino, california, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/apple",
            "current_employee_estimate": 164000,
            "total_employee_estimate": 164000
        },
        {
            "name": "Meta",
            "domain": "meta.com",
            "year_founded": 2004.0,
            "industry": "internet",
            "size_range": "10001+",
            "locality": "menlo park, california, united states",
            "country": "united states",
            "linkedin_url": "linkedin.com/company/meta",
            "current_employee_estimate": 87000,
            "total_employee_estimate": 87000
        }
    ]
    
    return pd.DataFrame(sample_data)

def load_csv_data(csv_path):
    """Load data from CSV file"""
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        print("Creating sample data...")
        return create_sample_data()
    
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Rename columns to match our schema
    column_mapping = {
        'name': 'name',
        'domain': 'domain',
        'year_founded': 'year_founded',
        'industry': 'industry',
        'size_range': 'size_range',
        'locality': 'locality',
        'country': 'country',
        'linkedin_url': 'linkedin_url',
        'current_employee_estimate': 'current_employee_estimate',
        'total_employee_estimate': 'total_employee_estimate'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    return df

def categorize_company_size(employee_count):
    """Categorize company size based on employee count"""
    if pd.isna(employee_count) or employee_count is None:
        return "Unknown"
    elif employee_count >= 10001:
        return "Large (10001+)"
    elif employee_count >= 1000:
        return "Medium (1000-10000)"
    else:
        return "Small (<1000)"

def ingest_data(es_client, df):
    """Ingest data into Elasticsearch"""
    index_name = "companies"
    batch_size = 100
    
    print(f"Ingesting {len(df)} records...")
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]
        
        # Prepare bulk data
        bulk_data = []
        for idx, row in batch.iterrows():
            # Convert row to dict and clean data
            doc = row.to_dict()
            
            # Handle NaN values
            for key, value in doc.items():
                if pd.isna(value):
                    doc[key] = None
                elif isinstance(value, float) and key == 'year_founded':
                    doc[key] = value if not pd.isna(value) else None
            
            # Categorize company size based on employee count
            employee_count = doc.get('current_employee_estimate')
            doc['size_category'] = categorize_company_size(employee_count)
            
            # Add metadata
            doc['tags'] = []
            doc['created_at'] = datetime.now().isoformat()
            doc['updated_at'] = datetime.now().isoformat()
            
            # Add to bulk data
            bulk_data.append({
                "index": {
                    "_index": index_name,
                    "_id": str(idx + 1)  # Use row number as ID
                }
            })
            bulk_data.append(doc)
        
        # Execute bulk insert
        try:
            response = es_client.bulk(body=bulk_data)
            if response['errors']:
                print(f"Some errors occurred in batch {i//batch_size + 1}")
                for item in response['items']:
                    if 'error' in item['index']:
                        print(f"Error: {item['index']['error']}")
            else:
                print(f"Successfully ingested batch {i//batch_size + 1} ({len(batch)} records)")
        except Exception as e:
            print(f"Error ingesting batch {i//batch_size + 1}: {str(e)}")
    
    print("Data ingestion completed!")

def create_tags_index(es_client):
    """Create tags index with sample tags"""
    index_name = "tags"
    
    # Delete index if it exists
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    
    mapping = {
        "mappings": {
            "properties": {
                "name": {"type": "keyword"},
                "description": {"type": "text"},
                "is_shared": {"type": "boolean"},
                "created_by": {"type": "keyword"},
                "created_at": {"type": "date"}
            }
        }
    }
    
    es_client.indices.create(index=index_name, body=mapping)
    
    # Add sample tags
    sample_tags = [
        {"name": "tech-leaders", "description": "Leading technology companies", "is_shared": True},
        {"name": "california-startups", "description": "Companies based in California", "is_shared": True},
        {"name": "enterprise-clients", "description": "Large enterprise companies", "is_shared": True},
        {"name": "potential-partners", "description": "Potential business partners", "is_shared": True},
        {"name": "competitors", "description": "Direct competitors", "is_shared": False},
        {"name": "targets", "description": "Target companies for acquisition", "is_shared": False}
    ]
    
    for i, tag in enumerate(sample_tags):
        tag['created_at'] = datetime.now().isoformat()
        es_client.index(index=index_name, id=i+1, body=tag)
    
    print(f"Created tags index with {len(sample_tags)} sample tags")

def main():
    """Main function"""
    print("Starting data ingestion pipeline...")
    
    try:
        # Connect to Elasticsearch
        es_client = connect_to_elasticsearch()
        
        # Create indices
        create_index_mapping(es_client)
        create_tags_index(es_client)
        
        # Load data
        csv_path = os.path.join("/app/data", "companies.csv")
        df = load_csv_data(csv_path)
        
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Ingest data
        ingest_data(es_client, df)
        
        # Verify data
        count_response = es_client.count(index="companies")
        print(f"Total records in Elasticsearch: {count_response['count']}")
        
        print("Data pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

