from service_objects.services import Service
from service_objects.fields import ModelField
from django.conf import settings
from django.db.models import F

from models_app.models.like import Like
from models_app.models.post import Post


class AddLikeService(Service):
    post = ModelField(Post)
    user = ModelField(settings.AUTH_USER_MODEL)

    def process(self):
        user = self.cleaned_data['user']
        post = self.cleaned_data['post']

        like, is_created = Like.objects.get_or_create(user=user, post=post)
        if is_created:
            post.total_likes = F('total_likes') + 1
            post.save()
        return like


class RemoveLikeService(Service):
    post = ModelField(Post)
    user = ModelField(settings.AUTH_USER_MODEL)

    def process(self):
        user = self.cleaned_data['user']
        post = self.cleaned_data['post']

        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()
            post.total_likes = F('total_likes') - 1
            post.save()
        except Like.DoesNotExist:
            ...


class UserHasLikedPostService(Service):
    post = ModelField(Post)
    user = ModelField(settings.AUTH_USER_MODEL)

    def process(self):
        user = self.cleaned_data['user']
        post = self.cleaned_data['post']

        return Like.objects.filter(user=user, post=post).exists()
