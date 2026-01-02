from opensearchpy import OpenSearch

index_name = 'chicago_art_installations'

def createIndex():
    client = OpenSearch(
        hosts=[{'host': 'localhost', 'port': 9200}],
        http_auth=('admin', 'admin'),  # If basic auth is enabled
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )
    print(client.info())

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

def addResultToIndex(document):
    client.index(index=index_name, body=document, id=1, refresh=True)