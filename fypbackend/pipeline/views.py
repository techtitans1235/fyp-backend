from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from django.conf import settings
from .utils.docx_utils import process_document_file
from .utils.excel_utils import convert_excel_to_json 
from .utils.docx_utils import process_doc_chunks
from .utils.background_task import run_in_background 
from django.core.cache import cache
from uuid import uuid4
from .utils.topic_entitiy_utils import generate_topics_entities
from django.db import connection
from rest_framework import status
from collections import defaultdict




class ProcessDocumentView(APIView):
    """
    API to process .docx files and return metadata and chunked text files.
    """ 
    def get(self , request):
        xlsx_file_name = 'ASR_Reports (Tajziakaar).xlsx'
        json_file_name = 'ASR_Reports (Tajziakaar).json'

        xlsx_file_path = os.path.join(settings.MEDIA_ROOT, 'ASR_Tajziakaar Reports', xlsx_file_name)
        json_file_path = os.path.join(settings.MEDIA_ROOT, 'ASR_Tajziakaar Reports', json_file_name)

        ouput_path = os.path.join(settings.MEDIA_ROOT, 'chunks')

        document_folder = os.path.join(settings.MEDIA_ROOT, 'ASR_Tajziakaar Reports')



        # convert_excel_to_json(xlsx_file_path , json_file_path )
        process_doc_chunks(ouput_path , json_file_path , document_folder)


        return Response({"message": "hello!" , "file": ouput_path})
    

class GenerateTopicsEntities(APIView):
    def get(self, request):
        json_file_name = 'ASR_Reports (Tajziakaar).json'
        json_file_path = os.path.join(settings.MEDIA_ROOT, 'ASR_Tajziakaar Reports', json_file_name)
        
        # Generate a unique key for this task
        progress_key = str(uuid4())
        
        # Start the background task
        run_in_background(generate_topics_entities, json_file_path, progress_key)
        
        # Return the progress key to the client
        return Response({"message": "Task started", "progress_key": progress_key})
    

class CheckTaskProgress(APIView):
    def get(self, request, progress_key):
        progress_data = cache.get(progress_key)
        
        if progress_data:
            return Response(progress_data)
        else:
            return Response({"status": "not_found", "message": "Invalid or expired progress key"}, status=404)


class MostFrequentEntityView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract start_date, end_date, and limit from the request data
        start_date = request.data.get("start_date", "2020-01-01")
        end_date = request.data.get("end_date", "2024-12-31")
        limit = request.data.get("limit", 5)

        # First, query to get the most frequent entities
        query_entities = """
            SELECT t.entity, COUNT(DISTINCT DATE(v.published_date)) AS distinct_days_count
            FROM pipeline_topic t
            JOIN pipeline_video v ON t.video_id = v.id
            WHERE v.published_date BETWEEN %s AND %s
            GROUP BY t.entity
            ORDER BY distinct_days_count DESC
            LIMIT %s;
        """
        
        try:
            # Open a cursor for the first query to get the most frequent entities
            with connection.cursor() as cursor:
                cursor.execute(query_entities, [start_date, end_date, limit])
                entities = cursor.fetchall()  # Fetch all entities

            if not entities:
                return Response({"message": "No entities found"}, status=status.HTTP_404_NOT_FOUND)
            
            print(entities)

            # Now, query for each entity to get the details
            results = []
            for entity in entities:
                entity_name = entity[0]
                
                # Open a new cursor for the second query to get details for the current entity
                with connection.cursor() as cursor:
                    query_details = """
                        SELECT DATE(v.published_date) AS specific_date, t.entity, COUNT(DISTINCT t.video_id) AS entity_count,
                               GROUP_CONCAT(t.content, ', ') AS contents
                        FROM pipeline_topic t
                        JOIN pipeline_video v ON t.video_id = v.id
                        WHERE t.entity = %s AND v.published_date BETWEEN %s AND %s
                        GROUP BY DATE(v.published_date), t.entity
                        ORDER BY specific_date;
                    """
                    
                    cursor.execute(query_details, [entity_name, start_date, end_date])
                    entity_details = cursor.fetchall()  # Fetch details for the entity

                # Format the entity details
                entity_data = {
                    "entity": entity_name,
                    "data": [
                        {"specific_date": row[0], "entity_count": row[2], "contents": row[3]}
                        for row in entity_details
                    ]
                }
                results.append(entity_data)

            # Return the results as a JSON response
            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MostFrequentEntitybyChannelView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract start_date, end_date, and limit from the request data
        start_date = request.data.get("start_date", "2020-01-01")
        end_date = request.data.get("end_date", "2024-12-31")
        limit = request.data.get("limit", 5)

        # First, query to get the most frequent entities
        query_entities = """
            SELECT t.entity, COUNT(DISTINCT DATE(v.published_date)) AS distinct_days_count
            FROM pipeline_topic t
            JOIN pipeline_video v ON t.video_id = v.id
            WHERE v.published_date BETWEEN %s AND %s
            GROUP BY t.entity
            ORDER BY distinct_days_count DESC
            LIMIT %s;
        """
        
        try:
            # Open a cursor for the first query to get the most frequent entities
            with connection.cursor() as cursor:
                cursor.execute(query_entities, [start_date, end_date, limit])
                entities = cursor.fetchall()  # Fetch all entities

            if not entities:
                return Response({"message": "No entities found"}, status=status.HTTP_404_NOT_FOUND)
            
            print(entities)

            # Now, query for each entity to get the details
            results = []
            for entity in entities:
                entity_name = entity[0]

                with connection.cursor() as cursor:
                    query = """
                        SELECT 
                            t.content AS topic_content, 
                            c.file_path AS chunk_path, 
                            v.file_name AS video_filename, 
                            ch.name AS channel_name,
                            ch.icon AS channel_icon
                        FROM 
                            pipeline_topic t
                        JOIN 
                            pipeline_chunk c 
                            ON t.chunk_id = c.id
                        JOIN 
                            pipeline_video v 
                            ON t.video_id = v.id
                        JOIN 
                            pipeline_channel ch 
                            ON v.channel_id = ch.id
                        WHERE 
                            t.entity = %s
                            AND v.published_date BETWEEN %s AND %s
                        ORDER BY 
                            ch.name ASC, v.file_name ASC, v.published_date ASC;
                    """

                    cursor.execute(query, [entity_name, start_date, end_date])
                    rows = cursor.fetchall()

                # Group rows by channel_name and then by video_filename
                grouped_data = defaultdict(lambda: defaultdict(list))
                channel_icons = {}
                for row in rows:
                    channel_name = row[3]
                    channel_icon = row[4]
                    video_filename = row[2]
                    grouped_data[channel_name][video_filename].append({
                        "topic_content": row[0],
                        "chunk_path": row[1],
                    })
                    channel_icons[channel_name] = channel_icon

                # Format the entity data
                entity_data = {
                    "entity": entity_name,
                    "channels": [
                        {
                            "channel_name": channel_name,
                            "channel_icon": channel_icons[channel_name],
                            "videos": [
                                {
                                    "video_filename": video_filename,
                                    "details": details
                                }
                                for video_filename, details in videos.items()
                            ],
                        }
                        for channel_name, videos in grouped_data.items()
                    ],
                }

                results.append(entity_data)

            # Return the results as a JSON response
            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChannelWiseEntityDistributionView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract start_date, end_date, and limit from the request data
        start_date = request.data.get("start_date", "2020-01-01")
        end_date = request.data.get("end_date", "2024-12-31")
        limit = request.data.get("limit", 5)
        channel_name = request.data.get("channel_name")

        # First, query to get the most frequent entities
        query_entities = """
            SELECT t.entity, COUNT(DISTINCT DATE(v.published_date)) AS distinct_days_count
            FROM pipeline_topic t
            JOIN pipeline_video v ON t.video_id = v.id
            WHERE v.published_date BETWEEN %s AND %s
            GROUP BY t.entity
            ORDER BY distinct_days_count DESC
            LIMIT %s;
        """
        
        try:
            # Open a cursor for the first query to get the most frequent entities
            with connection.cursor() as cursor:
                cursor.execute(query_entities, [start_date, end_date, limit])
                entities = cursor.fetchall()  # Fetch all entities

            if not entities:
                return Response({"message": "No entities found"}, status=status.HTTP_404_NOT_FOUND)
            
            print(entities)
            print(channel_name)

            # Now, query for each entity to get the details
            results = []
            for entity in entities:
                entity_name = entity[0]

                with connection.cursor() as cursor:
                    query = """
                        SELECT 
                            t.entity, 
                            COUNT(t.entity) AS entity_count
                        FROM 
                            pipeline_topic t
                        JOIN 
                            pipeline_video v 
                            ON t.video_id = v.id
                        JOIN 
                            pipeline_channel ch 
                            ON v.channel_id = ch.id
                        WHERE 
                            ch.name = %s
                            AND t.entity = %s
                            AND v.published_date BETWEEN %s AND %s

                        GROUP BY 
                            t.entity
                        ORDER BY 
                            entity_count DESC;
                    """

                    cursor.execute(query, [channel_name, entity_name, start_date , end_date])
                    rows = cursor.fetchall()

                grouped_data = defaultdict(lambda: defaultdict(int))
                for row in rows:
                    entity_name = row[0]
                    entity_count = row[1]
                    grouped_data[channel_name][entity_name] = entity_count

                # Convert grouped data into a list of results
                for channel, entities in grouped_data.items():
                    results.append({
                        "channel_name": channel,
                        "entities": [{"entity": entity, "count": count} for entity, count in entities.items()],
                    })

               

            # Return the results as a JSON response
            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllChannelsView(APIView):
    """
    API View to get all channel information.
    """

    def get(self, request):
        try:
            # Raw SQL query to fetch all channel information
            query = """
                SELECT id, name as channel_name, icon as channel_icon
                FROM pipeline_channel
                ORDER BY channel_name ASC;
            """
            
            with connection.cursor() as cursor:
                cursor.execute(query)
                channels = cursor.fetchall()

            # Format the data into a list of dictionaries
            channel_list = [
                {
                    "id": row[0],
                    "channel_name": row[1],
                    "channel_icon": row[2]
                }
                for row in channels
            ]

            return Response({"channels": channel_list}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)