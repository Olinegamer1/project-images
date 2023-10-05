from celery import shared_task
# from celery.utils.log import get_task_logger
from django.core.cache import cache
from project_images.celery import app


@shared_task(ignore_result=True)
def delete_post_delayed(post_id):
    from .models.post import Post

    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
    except Post.DoesNotExist:
        ...


def cancel_post_deletion(post_id):
    task_id = cache.get(post_id)
    if task_id:
        app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        cache.delete(post_id)
