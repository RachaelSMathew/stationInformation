from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import os

host = 's2cdyuddjlo8xk09s52j.us-east-2.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
region = 'us-east-2'
service = 'aoss'
credentials = boto3.Session().get_credentials() ## Render has it's own environment variables
auth = AWSV4SignerAuth(credentials, region, service)

isProduction = os.getenv('NODE_ENV', 'development') == 'production'

index_name = 'chicago_art_installations'
client = OpenSearch(
    hosts=[{'host': host, 'port': 443} if isProduction else {'host': 'localhost', 'port': 9200}],
    http_auth=auth if isProduction else ('admin', 'StrongPassword123!'),  # Use the correct password
    use_ssl=True,  # Enable SSL
    verify_certs=False,  # Don't verify certs for local dev
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    connection_class = RequestsHttpConnection if isProduction else None,
)

def createIndex():
    index_body = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "artwork_title": {"type": "text"},
                "description_of_artwork": {"type": "text"},
                "street_address": {"type": "text"},
                "media": {"type": "text"},
                "affiliated_or_commissioning": {"type": "text"},
                "year_installed": {"type": "text"},
                "artist_credit": {"type": "text"},
                "location_description": {"type": "text"},
            }
        }
    }

    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=index_body, ignore=400)

def addResultToIndex(muralCoords):
    for muralCoord in muralCoords:
        document = {
            "artwork_title": muralCoord.get('artwork_title', ''),
            "description_of_artwork": muralCoord.get('description_of_artwork', ''),
            "street_address": muralCoord.get('street_address', ''),
            "media": muralCoord.get('media', ''),
            "affiliated_or_commissioning": muralCoord.get('affiliated_or_commissioning', ''),
            "year_installed": muralCoord.get('year_installed', ''),
            "artist_credit": muralCoord.get('artist_credit', ''),
            "location_description": muralCoord.get('location_description', ''),
        }
        client.index(index=index_name, body=document, id=muralCoord['mural_registration_id'])

def searchIndex(query_string):
    query = {
        "query": {
            "multi_match": {
                "query": query_string,
                "type": "best_fields",
                "operator": "or",
                "fields": [
                    "artwork_title^2", 
                    "description_of_artwork^1.2", 
                    "street_address^1.1", 
                    "media^1", 
                    "affiliated_or_commissioning^1", 
                    "year_installed^1", 
                    "artist_credit^2", 
                    "location_description^1.1"
                ]
            }
        },
        "sort": [
            {
                "_score": {
                    "order": "desc"
                }
            }
        ],
        "size": 2000
    }

    response = client.search(
        body = query,
        index = 'chicago_art_installations',
    )
    return response
