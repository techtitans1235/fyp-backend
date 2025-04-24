from django.urls import path
from .views import ProcessDocumentView , GenerateTopicsEntities , CheckTaskProgress , MostFrequentEntityView , MostFrequentEntitybyChannelView , GetAllChannelsView , ChannelWiseEntityDistributionView

urlpatterns = [
    path('process-document', ProcessDocumentView.as_view(), name='process-document'),
    path('generate_topics_entities', GenerateTopicsEntities.as_view(), name='generate_topics_entities'),
    path('check_task_progress/<str:progress_key>', CheckTaskProgress.as_view(), name='check_task_progress'),
    path('most-frequent-entity-query', MostFrequentEntityView.as_view(), name='most-frequent-entity-query'),
    path('most-frequent-entity-query-byChannel', MostFrequentEntitybyChannelView.as_view(), name='most-frequent-entity-query-byChannel'),
    path('get_all_channels', GetAllChannelsView.as_view(), name='get_all_channels'),
    path('channel_wise_entity', ChannelWiseEntityDistributionView.as_view(), name='channel_wise_entity'),
]