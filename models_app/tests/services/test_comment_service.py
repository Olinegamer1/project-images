from django.test import TestCase
from django.contrib.auth.models import User

from models_app.models.post import Post
from models_app.models.comment import Comment
from models_app.services.comments.create import CreateCommentService
from models_app.services.comments.update import UpdateCommentService
from models_app.services.comments.delete import DeleteCommentService


class CommentServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        self.post = Post.objects.create(
            title='Test Post',
            description='This is a test post',
            user=self.user,
        )

    def _create_comment(self, text, parent_comment=None):
        return CreateCommentService.execute({
            'user': self.user,
            'post': self.post,
            'text': text,
            'parent_comment': parent_comment
        })

    def _update_comment(self, comment, text):
        UpdateCommentService.execute({
            'comment': comment,
            'text': text
        })

    def _delete_comment(self, comment):
        DeleteCommentService.execute({
            'comment': comment
        })

    def test_create_comment(self):
        initial_comment_count = self.post.comments.count()
        comment_text = 'This is a test comment'
        comment = self._create_comment(comment_text)
        updated_comment_count = self.post.comments.count()

        self.assertEqual(updated_comment_count, initial_comment_count + 1)
        self.assertEqual(comment.body, comment_text)

    def test_update_comment(self):
        initial_comment_text = 'This is a test comment'
        comment = self._create_comment(initial_comment_text)
        updated_comment_text = 'This is a updated comment'
        self._update_comment(comment, updated_comment_text)
        comment_body = comment.body

        self.assertNotEquals(comment_body, initial_comment_text)
        self.assertEqual(comment_body, updated_comment_text)

    def test_add_reply_to_comment(self):
        parent_comment_text = 'This is a test comment'
        parent_comment = self._create_comment(parent_comment_text)
        reply_text = 'This is a answer to parent comment'
        reply = self._create_comment(reply_text, parent_comment=parent_comment)
        parent_comment_replies_count = parent_comment.replies.count()

        self.assertEqual(parent_comment_replies_count, 1)
        self.assertEqual(reply.body, reply_text)
        self.assertEqual(parent_comment, reply.parent_comment)

    def test_delete_comment(self):
        initial_comment_text = 'This is a test comment'
        comment = self._create_comment(initial_comment_text)

        self.assertIsNotNone(comment)

        self._delete_comment(comment)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(pk=comment.pk)

    def test_delete_comment_with_reply(self):
        parent_comment_text = 'This is a test comment'
        parent_comment = self._create_comment(parent_comment_text)

        reply_text = 'This is a answer to parent comment'
        reply = self._create_comment(reply_text, parent_comment=parent_comment)

        with self.assertRaises(ValueError):
            DeleteCommentService.execute({
                'comment': parent_comment
            })

    def tearDown(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()
