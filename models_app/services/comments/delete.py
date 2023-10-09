from service_objects.fields import ModelField
from service_objects.services import Service

from models_app.models.comment import Comment


class DeleteCommentService(Service):
    comment = ModelField(Comment)

    def process(self):
        comment = self.cleaned_data['comment']

        if not Comment.objects.filter(parent_comment=comment).exists():
            comment.delete()
        else:
            raise ValueError("Can't delete comment with replies")
