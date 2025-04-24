# serializers.py
from rest_framework import serializers
from .models import Channel, Video, Chunk, Topic

# Channel Serializer
class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name']


# Video Serializer
class VideoSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer()  # Nested ChannelSerializer to display channel details

    class Meta:
        model = Video
        fields = ['id', 'channel', 'name', 'url', 'file_name', 'published_date', 'duration']

    # Optional validation for unique video name
    def validate_name(self, value):
        if Video.objects.filter(name=value).exists():
            raise serializers.ValidationError("Video name must be unique.")
        return value


# Chunk Serializer
class ChunkSerializer(serializers.ModelSerializer):
    video = VideoSerializer()  # Nested VideoSerializer to display video details

    class Meta:
        model = Chunk
        fields = ['id', 'video', 'file_path']

    # Optional validation for unique file path
    def validate_file_path(self, value):
        if Chunk.objects.filter(file_path=value).exists():
            raise serializers.ValidationError("File path must be unique.")
        return value


# Topic Serializer
class TopicSerializer(serializers.ModelSerializer):
    video = VideoSerializer()  # Nested VideoSerializer to display video details
    chunk = ChunkSerializer()  # Nested ChunkSerializer to display chunk details

    class Meta:
        model = Topic
        fields = ['id', 'video', 'chunk', 'content', 'entity']

    # Optional validation for entity field
    def validate_entity(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Entity field cannot be empty.")
        return value
