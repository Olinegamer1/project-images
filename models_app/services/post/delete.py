from django import forms
from django.core.cache import cache
from service_objects.services import Service

from project_images.settings import REMOVAL_DELAY_POST_IN_SECONDS
from models_app.tasks import delete_post_delayed


class PostDeletionService(Service):
    post_id = forms.IntegerField()

    def process(self):
        post_id = self.cleaned_data['post_id']
        self.schedule_deletion(post_id, REMOVAL_DELAY_POST_IN_SECONDS)

    def schedule_deletion(self, post_id, delay_seconds):
        task = delete_post_delayed.apply_async(kwargs={'post_id': post_id}, countdown=delay_seconds)
        cache.set(post_id, task.id)
