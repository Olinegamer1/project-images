from django.conf import settings
from service_objects.fields import ModelField
from service_objects.services import Service

from models_app.models.like import Like
from models_app.models.post import Post


class UserHasLikedPostService(Service):
    post = ModelField(Post)
    user = ModelField(settings.AUTH_USER_MODEL)

    def process(self):
        user = self.cleaned_data['user']
        post = self.cleaned_data['post']

        return Like.objects.filter(user=user, post=post).exists()
