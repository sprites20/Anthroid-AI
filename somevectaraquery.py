import requests
import json

url = "https://api.vectara.io/v1/query"

user_query = "latest LLMs April"
payload = json.dumps({
  "query": [
    {
      "query": f"{user_query}",
      "start": 0,
      "numResults": 10,
      "contextConfig": {
        "sentences_before": 3,
        "sentences_after": 3,
        "start_tag": "<b>",
        "end_tag": "</b>"
      },
      "corpusKey": [
        {
          "corpus_id": 2
        }
      ],
      "summary": [
        {
          "max_summarized_results": 10,
          "response_lang": "en"
        }
      ]
    }
  ]
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'customer-id': '4239971555',
  'x-api-key': 'zwt__LjU4zVE9TBF1tU4SbJ0rrjT1QWwI2sXXp4iGQ'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
json_result = json.loads(response.text)
print(f"Summary: {json_result['responseSet'][0]['summary'][0]['text']}")
print(f"Factual Consistency: {json_result['responseSet'][0]['summary'][0]['factualConsistency']['score']}")