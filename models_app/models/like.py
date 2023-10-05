from django.db import models
from django.conf import settings
from .post import Post


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='likes',
                             related_query_name='user_liked',
                             blank=True,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             related_name='likes',
                             related_query_name='post_liked',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'
