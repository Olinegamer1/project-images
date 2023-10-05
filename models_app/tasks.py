from celery import shared_task

from models_app.models.post import Post


@shared_task(ignore_result=True)
def delete_post_delayed(post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
    except Post.DoesNotExist:
        ...
