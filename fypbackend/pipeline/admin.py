from django.contrib import admin
from .models import Channel, Video, Chunk, Topic

# Admin for Channel
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Displaying all attributes of Channel

# Admin for Video
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'name', 'url', 'file_name', 'published_date', 'duration')  # All attributes of Video

# Admin for Chunk
@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'file_path')  # All attributes of Chunk

# Admin for Topic
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'chunk', 'content', 'entity')  # All attributes of Topic
