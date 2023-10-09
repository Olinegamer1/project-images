from django import forms
from django.conf import settings
from service_objects.fields import ModelField
from service_objects.services import Service

from models_app.models.comment import Comment
from models_app.models.post import Post


class CreateCommentService(Service):
    user = ModelField(settings.AUTH_USER_MODEL)
    post = ModelField(Post)
    text = forms.CharField(max_length=400)
    parent_comment = ModelField(Comment, required=False)

    def process(self):
        return Comment.objects.create(
            user=self.cleaned_data['user'],
            body=self.cleaned_data['text'],
            post=self.cleaned_data['post'],
            parent_comment=self.cleaned_data['parent_comment']
        )
