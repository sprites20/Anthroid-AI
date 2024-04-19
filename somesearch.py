from openai import OpenAI
from googlesearch import search

from bs4 import BeautifulSoup

import os
import re
import requests
import json


from datetime import datetime, timedelta
from unstructured.cleaners.translate import translate_text

#a = translate_text("Ich bin ein Berliner!")
#print(a)

TOGETHER_API_KEY = "5391e02b5fbffcdba1e637eada04919a5a1d9c9dfa5795eafe66b6d464d761ce"


client = OpenAI(
  api_key=TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)

# Get current UTC time
utc_time = datetime.utcnow()
import random

# List of interesting search queries
search_queries = [
    "Python programming tutorials",
    "Space exploration news",
    "Artificial intelligence research papers",
    "Submarine technology advancements",
    "Philosophical questions about life",
    "Best rap lyrics of all time",
    "Real-time voice recognition software",
    "3D rendering techniques in Python",
    "Popular books on theology",
    "SQL best practices in industry",
    "Latest technology trends",
    "Historical events timeline",
    "Famous quotes about success",
    "Healthy recipes for breakfast",
    "How to improve mental health",
    "Top travel destinations in the world",
    "Upcoming movie releases",
    "DIY home improvement projects",
    "Best practices for time management",
    "Interesting facts about animals",
    "Machine learning algorithms comparison",
    "Popular coding languages in 2024",
    "Financial planning for retirement",
    "Effective communication skills",
    "Best podcasts for personal development",
    "How to start a small business",
    "Healthy habits for a productive day",
    "Interesting facts about space exploration",
    "Travel tips for first-time travelers",
    "History of ancient civilizations"
]

def get_random_search_query():
    return random.choice(search_queries)

# Example usage
random_search_query = get_random_search_query()
print("Random search query:", random_search_query)

user_prompt = "Latest news about LLMs"
"""
We can later query Vectara about the html
"""

def get_search_query(user_prompt):
    #user_prompt = random_search_query
    # Format UTC time
    formatted_utc_time = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    chat_completion = client.chat.completions.create(
      messages=[
        {
          "role": "system",
          "content": "You want to search the web, and wants to Google about the topic. You answer in search engine query or multiple. Maximum is 1, EACH query is separated by brackets, {query1} ",
        },
        {
          "role": "user",
          "content": f"Date Now:{formatted_utc_time}\n{user_prompt}",
        }
      ],
      model="mistralai/Mixtral-8x7B-Instruct-v0.1"
    )

    result = chat_completion.choices[0].message.content
    
    #print(result)
    # Regular expression to match text inside curly braces
    pattern = r"\{(.*?)\}"
    
    # Find all matches
    matches = re.findall(pattern, result)
    

    # Find all matches
    matches = re.findall(pattern, result)

    # Print the matches
    matches.insert(0, user_prompt)
    print(matches)
    return matches

def vectara_search_web_and_process(matches):
    # Create a dictionary to represent the JSON object
    json_data = {
        "user_prompt": user_prompt,
        "datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "queries": {}
    }
    # Define a custom user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    #We need to handle empty cases
    for i in matches:
        query = i
        somesearch = search(query, advanced=True, num_results=1)
        print(query)
        json_data["queries"][query] = []
        print(somesearch)
        for i in somesearch:
            url = i.url
            now = datetime.now()
            print(datetime.now().strftime("%m/%d/%y %I:%M %p"))
            date_downloaded = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            print(date_downloaded)
            print(url)

            #print(i)
            
            #Will soon use
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            #Translate the text
            text = translate_text(text)
            json_data["queries"][query].append({"url": url, "text": text})
            
            date_uploaded = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            parsed_url = re.sub(r'[/:.]', '_', url)
            metadata_args = {
                "date_downloaded" : re.sub(r'[/:.]', '_', date_downloaded),
                "user_prompt" : user_prompt,
                "url" : parsed_url
            }
            
            temp_json = {
                "user_prompt": user_prompt,
                "date_downloaded": re.sub(r'[/:.]', '_', date_downloaded),
                "date_uploaded": re.sub(r'[/:.]', '_', date_uploaded),
                "query": query,
                "url": parsed_url,
                "text": text,
                "title": i.title,
                "description": i.description,
            }
            send_one_doc_to_vectara(temp_json, metadata_args)
            
            #print(text)
    #print(json_data)

    return json_data, metadata_args

def send_one_doc_to_vectara(json_data, metadata_args):
    metadata = {
        #"metadata_key": "metadata_value",
        "date_downloaded": metadata_args["date_downloaded"],
        "date_uploaded": re.sub(r'[/:.]', '_', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")),
        "user_prompt": metadata_args["user_prompt"],
        "url" : metadata_args["url"],
    }
    json_data_bytes = json.dumps(json_data).encode('utf-8')
    url = "https://api.vectara.io/v1/upload?c=4239971555&o=2"
    headers = {
        'x-api-key': 'zwt__LjU4zVE9TBF1tU4SbJ0rrjT1QWwI2sXXp4iGQ'
    }
    now = datetime.utcnow().strftime("%Y_%m_%d %H_%M_%S UTC")
    # Save the JSON-formatted string to a file
    with open(f"{metadata['url']}_{metadata['date_uploaded']}.json", "w") as file:
        file.write(json.dumps(json_data))
    files = {
        "file": (f"{metadata['date_uploaded']}|{metadata['url']}", json_data_bytes, 'rb'),
        "doc_metadata": (None, json.dumps(metadata)),  # Replace with your metadata
    }
    response = requests.post(url, headers=headers, files=files)
    print(response.text)

#Send individual links to Vectara
def send_doc_to_vectara(json_data, metadata_args):
    
    metadata = {
        #"metadata_key": "metadata_value",
        "date_uploaded": re.sub(r'[/:.]', '_', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")),
        "user_prompt": metadata_args["user_prompt"],
    }
    json_data_bytes = json.dumps(json_data).encode('utf-8')
    url = "https://api.vectara.io/v1/upload?c=4239971555&o=2"
    headers = {
        'x-api-key': 'zwt__LjU4zVE9TBF1tU4SbJ0rrjT1QWwI2sXXp4iGQ'
    }
    now = datetime.utcnow().strftime("%Y_%m_%d %H_%M_%S UTC")
    # Save the JSON-formatted string to a file
    with open(f"User Prompt: {metadata['user_prompt']}; {metadata['date_uploaded']}.json", "w") as file:
        file.write(json.dumps(json_data))
    files = {
        "file": (f"User Prompt: {metadata['user_prompt']}; {metadata['date_uploaded']}", json_data_bytes, 'rb'),
        "doc_metadata": (None, json.dumps(metadata)),  # Replace with your metadata
    }
    response = requests.post(url, headers=headers, files=files)
    print(response.text)

def vectara_query(user_query):
    url = "https://api.vectara.io/v1/query"

    user_query = f"{user_query}"
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

#Generate search queries with LLM and links from Google
#matches = get_search_query(random_search_query)
query = user_prompt
matches = get_search_query(query)
#Download text from links and pack to json
json_data, metadata_args = vectara_search_web_and_process(matches)

#Send doc to vectara
send_doc_to_vectara(json_data, metadata_args)

#Query the thing
vectara_query(query)


#LLM Logic
"""
The program should:
1. Gather user intent, examples, what is the user searching for,

2. Ask LLM to generate a search engine query based on the user intent
Use together AI

3. Get search query

4. Google Search

5. Download links

6. Generate json from the links
{
"user_prompt" : ""
"datetime" : ""
"queries": {}

}
7. Send the link text to Vectara

8. Aggregate the results
"""


"""
1. Recognize Face half

1. Record voice half

2. Recognize Voice half

2. Record webcam half

3. Whenever speaking recognize speaker. With face

3. And voice.

3. Output to json
"""

"""
Local Embeddings
1. Save documents from web.

2. Try to embed things

3. Partition with unstructured

"""

"""


"""