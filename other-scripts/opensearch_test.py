from opensearchpy import OpenSearch

host = "search-dining-concierge-search-a6o2oqa3vm6v5qef3pyjb3hhrq.us-east-1.es.amazonaws.com"

es = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True
)

# Test
cuisine = "japanese"

resp = es.search(index="restaurants", body={
    "query": {
        "match": {
            "Cuisine": cuisine
        }
    }
})

print(resp["hits"]["total"])
for hit in resp["hits"]["hits"][:5]:
    print(hit["_source"])