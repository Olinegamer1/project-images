from django.db import models
from django.conf import settings
from models_app.models.post import Post


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    body = models.CharField(max_length=400)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='users_comments',
                             related_query_name='user_comment',
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             related_name='posts_comments',
                             related_query_name='post_comment',
                             on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self',
                                       related_name='replies',
                                       related_query_name='reply',
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ['-created']

    def __str__(self):
        return f'Comment by {self.user.username} on post {self.post}'
