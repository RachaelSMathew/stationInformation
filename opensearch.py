from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import os

host = '1oh1z3rqlx7kculsnqqf.us-east-2.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
region = 'us-east-2'
service = 'aoss'
credentials = boto3.Session().get_credentials()
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
                "searchableContent": {"type": "text"},
            }
        }
    }

    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=index_body, ignore=400)

def addResultToIndex(muralCoords):
    for muralCoord in muralCoords:
        document = {
            "searchableContent": muralCoord.get('artwork_title','') +  muralCoord.get('description_of_artwork', '') +  muralCoord['street_address'] + muralCoord.get('media', '') + muralCoord.get('affiliated_or_commissioning','')+muralCoord.get('year_installed','')+muralCoord['artist_credit'] + muralCoord.get('location_description', '')
        }
        client.index(index=index_name, body=document, id=muralCoord['mural_registration_id'], refresh=True)

def searchIndex(query_string):
    query = {
        "query": {
            "query_string": {
                "query": "*"+query_string+"*", ## remove all special characters
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