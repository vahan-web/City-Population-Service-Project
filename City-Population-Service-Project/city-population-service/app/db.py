import os
from elasticsearch import Elasticsearch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self):
        # Get ES connection details from environment variables with defaults
        es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
        es_port = os.environ.get('ELASTICSEARCH_PORT', '9200')
        es_user = os.environ.get('ELASTICSEARCH_USER', '')
        es_password = os.environ.get('ELASTICSEARCH_PASSWORD', '')
        
        # Build connection URL
        if es_user and es_password:
            self.es_url = f"http://{es_user}:{es_password}@{es_host}:{es_port}"
        else:
            self.es_url = f"http://{es_host}:{es_port}"
        
        self.es = None
        self.index_name = "cities"
        
    def connect(self):
        """Establish connection to Elasticsearch"""
        try:
            self.es = Elasticsearch(self.es_url)
            logger.info("Connected to Elasticsearch")
            
            # Create index if it doesn't exist
            if not self.es.indices.exists(index=self.index_name):
                self.es.indices.create(
                    index=self.index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "name": {"type": "keyword"},
                                "population": {"type": "long"}
                            }
                        }
                    }
                )
                logger.info(f"Created index: {self.index_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            return False
    
    def upsert_city(self, city_name, population):
        """Insert or update a city's population"""
        try:
            # Normalize city name to lowercase for consistency
            city_name = city_name.lower()
            
            # Prepare document
            doc = {
                "name": city_name,
                "population": population
            }
            
            # Update with upsert
            self.es.index(
                index=self.index_name,
                id=city_name,
                document=doc
            )
            logger.info(f"Upserted city: {city_name} with population: {population}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert city: {str(e)}")
            return False
    
    def get_city_population(self, city_name):
        """Get a city's population"""
        try:
            # Normalize city name to lowercase for consistency
            city_name = city_name.lower()
            
            result = self.es.get(
                index=self.index_name,
                id=city_name
            )
            
            if result and result.get('found'):
                return result['_source']['population']
            return None
        except Exception as e:
            logger.error(f"Failed to get city population: {str(e)}")
            return None

# Create a singleton instance
es_client = ElasticsearchClient()