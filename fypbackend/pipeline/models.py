from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon = models.CharField(max_length=255, null=True, blank=True)  # Add this field
    
    def __str__(self):
        return self.name


# Video Model
class Video(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    name = models.CharField(max_length=255 , unique=True)
    url = models.URLField()
    file_name = models.CharField(max_length=255)
    published_date = models.DateTimeField()
    duration = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.url} {self.file_name} {self.published_date} {self.duration}"


# Chunk Model
class Chunk(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='chunks')
    file_path = models.CharField(max_length=255 , unique=True)
    
    def __str__(self):
        return f"Chunk {self.file_path} for {self.video.name}"


# Topic Model with a reference to Chunk
class Topic(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='topics')
    chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE, related_name='topics')  # New field linking to Chunk
    content = models.TextField()
    entity = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.content} {self.entity}"
