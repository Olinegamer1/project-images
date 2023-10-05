from service_objects.services import Service
from service_objects.fields import ModelField
from django.conf import settings
from django import forms
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


class UpdateCommentService(Service):
    comment = ModelField(Comment)
    text = forms.CharField(max_length=400)

    def process(self):
        comment = self.cleaned_data['comment']
        comment.body = self.cleaned_data['text']
        comment.save()
        return comment


class DeleteCommentService(Service):
    comment = ModelField(Comment)

    def process(self):
        comment = self.cleaned_data['comment']

        if not Comment.objects.filter(parent_comment=comment).exists():
            comment.delete()
        else:
            raise ValueError("Can't delete comment with replies")