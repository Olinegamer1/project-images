from django.db import transaction

from models_app.models.post import Post
from models_app.services.post.delete import PostDeletionService
from models_app.services.post.cancel_delete import CancelPostDeletionService


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
