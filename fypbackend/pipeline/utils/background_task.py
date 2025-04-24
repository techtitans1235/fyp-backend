import threading
import json
import os
from .topic_entitiy_utils import generate_topics_entities
from django.conf import settings
from django.core.cache import cache




   
def run_in_background(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True  # Ensures the thread ends when the main program ends
    thread.start()