from django.core.cache import cache
from django.db import transaction
from django import forms
from service_objects.fields import ModelField
from service_objects.services import Service

from models_app.models.post import Post
from models_app.tasks import delete_post_delayed
from project_images.celery import app
from project_images.settings import REMOVAL_DELAY_POST_IN_SECONDS


class PostAdminService:
    @staticmethod
    def _process_posts(posts, action_function, post_service=None):
        with transaction.atomic():
            for post in posts:
                action_function(post)
                if post_service:
                    post_service.execute({'post_id': post.id})
                post.save()

    @staticmethod
    def reject(posts):
        PostAdminService._process_posts(
            posts=posts,
            action_function=Post.reject_by_admin,
            post_service=PostDeletionService
        )

    @staticmethod
    def approve(posts):
        PostAdminService._process_posts(
            posts=posts,
            action_function=Post.approve_by_admin
        )

    @staticmethod
    def restore(posts):
        PostAdminService._process_posts(
            posts=posts,
            action_function=Post.restore_by_admin,
            post_service=CancelPostDeletionService
        )


class PostDeletionService(Service):
    post_id = forms.IntegerField()

    def process(self):
        post_id = self.cleaned_data['post_id']
        self.schedule_deletion(post_id, REMOVAL_DELAY_POST_IN_SECONDS)

    def schedule_deletion(self, post_id, delay_seconds):
        task = delete_post_delayed.apply_async(kwargs={'post_id': post_id}, countdown=delay_seconds)
        cache.set(post_id, task.id)


class CancelPostDeletionService(Service):
    post_id = forms.IntegerField()

    def process(self):
        post_id = self.cleaned_data['post_id']
        task_id = cache.get(post_id)
        app.control.revoke(task_id, terminate=True)
