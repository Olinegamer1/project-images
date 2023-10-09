from django import forms
from django.core.cache import cache
from service_objects.services import Service

from project_images.celery import app


class CancelPostDeletionService(Service):
    post_id = forms.IntegerField()

    def process(self):
        post_id = self.cleaned_data['post_id']
        task_id = cache.get(post_id)
        app.control.revoke(task_id, terminate=True)
