import json
from .llama_api import generate_entity  , generate_topics , generate_topic_entity
from django.core.cache import cache
from uuid import uuid4
from ..models import Channel , Video , Chunk , Topic




def read_txt_file(file_path):
    try:
        with open(file_path, 'r' , encoding="utf-8") as file:
            data = file.read()  # Read the entire file content
        return data
    except FileNotFoundError:
        return "File not found."

def format_topics(result):
    topics = {}
    content_lines = result['extracted_topics'].split('\n')
    
    for idx, line in enumerate(content_lines, start=1):
        parts = line.split(" ")
        content = " ".join(parts[1:]) 
        entity = parts[1] 

        topics[f"topic{idx}"] = {
            "content": content,
            "entity": ""
        }

    return topics

def create_channel_video(data):
    # Extract the necessary fields
    channel_name = data.get('Channel')
    
    # Get or create the channel
    channel, created = Channel.objects.get_or_create(name=channel_name)

    # Create the video linked to the channel
    video = Video.objects.create(
        channel=channel,
        name=data.get('Named as'),
        url=data.get('URL'),
        file_name=data['Audio Metadata'].get('Audio File Name'),
        published_date=data['Audio Metadata'].get('Published Date'),
        duration=data['Audio Metadata'].get('Audio File Duration')  
    )
    
    return channel, video

def create_chunk_entity(video, file_path, data):
    print("chunk...................")
    chunk = None  # Initialize variable to None to ensure it's defined if an exception occurs

    try:
        # Create the chunk using keyword arguments
        chunk = Chunk.objects.create(video=video, file_path=file_path)
        
        if chunk:
            print("chunk...................", chunk.id)
        
        # Create the topics using keyword arguments
        Topic.objects.create(
            video=video,
            chunk=chunk,
            content=data['topic1']['content'],
            entity=data['topic1']['entity']
        )
        Topic.objects.create(
            video=video,
            chunk=chunk,
            content=data['topic2']['content'],
            entity=data['topic2']['entity']
        )
        Topic.objects.create(
            video=video,
            chunk=chunk,
            content=data['topic3']['content'],
            entity=data['topic3']['entity']
        )
        
    except Exception as e:
        # Handle any exceptions that occur
        print(f"An error occurred: {e}")
    
    return chunk



def convert_chunk_data_generic(data):
    # Extract chunk id from filePath
    file_path = data.get('filePath')
    chunk_id = file_path.split('/')[-1].split('_')[-1].split('.')[0]
    
    # Extract topics without updating them manually
    topics = data.get('topics', {})

    # Create the chunk data dictionary
    chunk_data = {
        "chunk_id": chunk_id,
        "file_path": file_path,
        "topics": topics
    }

    return chunk_data

# def generate_entity(result):
#     print(result)
#     for res in result:
#         outputs = generate_entities(result[res]['content'])
#         generated_entity = outputs["generated_entity"]
#         result[res]['entity'] = generated_entity
#     print(result)

#     return result





def generate_topics_entities( json_file, progress_key):

    cache.set(progress_key, {"status": "in_progress", "progress": 0}, timeout=None)  # Set initial progress

    try:
        with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                total_chunks = sum(len(info["chunks"]) for info in data)  # Total chunks for progress calculation
                processed_chunks = 0

                for i , info in enumerate(data):
                    channel , video = create_channel_video(info)

                    # videoId = create_video_if_not_exists(channelId , videoData)
                    for j ,  chunk in enumerate(info["chunks"]):
                        file_path = info["chunks"][chunk]["filePath"]
                        print(file_path)
                        urdu_text = read_txt_file(file_path)
                        # outputs = generate_topics(urdu_text)

                        # result = outputs["extracted_topics"]
                        # result = format_topics(outputs)

                        # result = generate_entity(result)

                        result = generate_topic_entity(urdu_text)

                        create_chunk_entity(video , file_path , result)

                        processed_chunks += 1
                        progress = int((processed_chunks / total_chunks) * 100)
                        cache.set(progress_key, {"status": "in_progress", "progress": progress}, timeout=None)

                        # info["chunks"][chunk]["topics"] = result
                    
                        # create_chunk_if_not_exists(videoId , convert_chunk_data_generic(info["chunks"][chunk]))
                        
                        print(result)
                        
                    # with open(json_file, 'w', encoding='utf-8') as outfile:
                    #     json.dump(data, outfile, indent=4, ensure_ascii=False)
                    #     print(f"Updated metadata saved to {json_file}")
        cache.set(progress_key, {"status": "completed", "progress": 100}, timeout=None)  # Mark as completed

    except Exception as e:
        cache.set(progress_key, {"status": "failed", "error": str(e)}, timeout=None)
                        
                        


        
