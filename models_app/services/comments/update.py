from django import forms
from service_objects.fields import ModelField
from service_objects.services import Service

from models_app.models.comment import Comment


class UpdateCommentService(Service):
    comment = ModelField(Comment)
    text = forms.CharField(max_length=400)

    def process(self):
        comment = self.cleaned_data['comment']
        comment.body = self.cleaned_data['text']
        comment.save()
        return comment
