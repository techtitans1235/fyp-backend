import requests
import time
import json

BASE_URL = ""

def format_topics(result):
    topics = {}
    
    for idx, line in enumerate(result, start=1):

        topics[f"topic{idx}"] = {
            "content": line,
            "entity": ""
        }

    return topics

def extract_result(api_response):
    """Extract result from the API response."""
    if "result" not in api_response:
        return "Error: 'result' not found in the response."
    result = api_response["result"]

    if isinstance(result, list) and len(result) > 0:
        for item in result:
            if item["role"] == "assistant":
                content = item["content"]
                if "\n" not in content:
                    return content.strip()

        # If content contains multiple lines, return as a list of topics
        for item in result:
            if item["role"] == "assistant":
                content = item["content"]
                topics = [line.strip() for line in content.split("\n") if line.strip()]
                return topics

    return "Error: Unable to parse response."

def generate_entity1(result):
    print(result)
    for res in result:
        generated_entity = generate_entity(result[res]['content'])
        result[res]['entity'] = generated_entity
    print(result)

    return result

def generate_entity(text):
    """Generate entities from the provided text."""
    payload = {"text": text}
    try:
        response = requests.post(f"{BASE_URL}/generate_entity", json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        api_response = response.json()
        return extract_result(api_response)
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def generate_topics(text):
    """Generate topics from the provided text."""
    payload = {"text": text}
    try:
        response = requests.post(f"{BASE_URL}/generate_topics", json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        api_response = response.json()
        return extract_result(api_response)
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    
def generate_topic_entity(urdu_text):
    topics = generate_topics(urdu_text)
    topics = format_topics(topics)
    result = generate_entity1(topics)
    print("Extracted Entity:", result)
    return result


