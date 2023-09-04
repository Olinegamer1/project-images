from celery import shared_task
# from celery.utils.log import get_task_logger
from django.core.cache import cache
from project_images.celery import app

# logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def delete_post_delayed(post_id):
    from .models.post import Post

    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
        # logger.info(f'Post with id {post_id} deleted successfully.')
    except Post.DoesNotExist:
        ...
        # logger.warning(f'Post with id {post_id} not found.')


def cancel_post_deletion(post_id):
    task_id = cache.get(post_id)
    if task_id:
        app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        cache.delete(post_id)
        # logger.info(f'Post with id {post_id} restored successfully.')
    else:
        ...
        # logger.warning(f'Task not found for post id {post_id}.')
