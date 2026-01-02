from opensearchpy import OpenSearch

index_name = 'chicago_art_installations'
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'StrongPassword123!'),  # Use the correct password
    use_ssl=True,  # Enable SSL
    verify_certs=False,  # Don't verify certs for local dev
    ssl_assert_hostname=False,
    ssl_show_warn=False,
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
            "query": query_string ## remove all special characters
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