import json
import requests
def get_question(query):
    api_key = "AIzaSyDuWYpuIfwyA3Z6iEjYS-C2_E0-2xI8l-U"
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    search_query = query
    params = {
        "query": search_query,
        "languageCode": "en",
        "pageSize": 10,
        "maxAgeDays": 365,
        "key": api_key
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        filtered = []
        for item in data.get('claims', []):  # Safely access 'claims'
            if isinstance(item, dict):  # Ensure 'item' is a dictionary
                if 'claimReview' in item and isinstance(item['claimReview'], list):
                    if item['claimReview'][0].get('textualRating') in ['True', 'False']:
                        filtered.append(item)
        print(filtered)
        print(f"{filtered[0]['text']} | {filtered[0]['claimReview'][0]['textualRating']}")


    else:
        print(f"Error fetching data: {r.status_code} {r.text}")

get_question('Abortion')
