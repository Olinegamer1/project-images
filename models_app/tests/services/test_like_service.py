from django.test import TestCase
from django.contrib.auth.models import User

from models_app.models.like import Like
from models_app.models.post import Post, Status
from models_app.services.like.has_like import UserHasLikedPostService
from models_app.services.like.remove import RemoveLikeService
from models_app.services.like.add import AddLikeService


class LikeServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.post = Post.objects.create(
            title='Test Post',
            description='This is a test post',
            user=self.user,
            status=Status.PUBLISHED
        )
        self.inputs = {
            'post': self.post,
            'user': self.user
        }

    def test_add_like(self):
        initial_like_count = Like.objects.filter(post=self.post).count()

        self.assertEqual(initial_like_count, self.post.total_likes)

        AddLikeService.execute(self.inputs)

        updated_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(updated_like_count, initial_like_count + 1)

        self.post.refresh_from_db(fields=('total_likes',))
        self.assertEqual(updated_like_count, self.post.total_likes)

    def test_add_duplicate_like(self):
        initial_like_count = Like.objects.filter(post=self.post).count()

        for _ in range(2):
            AddLikeService.execute(self.inputs)

        updated_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(updated_like_count, initial_like_count + 1)

        self.post.refresh_from_db(fields=('total_likes',))
        self.assertEqual(updated_like_count, self.post.total_likes)

    def test_remove_like(self):
        initial_like_count = Like.objects.filter(post=self.post).count()

        AddLikeService.execute(self.inputs)
        after_add_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(initial_like_count + 1, after_add_like_count)

        RemoveLikeService.execute(self.inputs)
        after_remove_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(initial_like_count, after_remove_like_count)

    def test_user_has_liked_post(self):
        initial_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(initial_like_count, 0)

        self.assertEqual(UserHasLikedPostService.execute(self.inputs), False)

        AddLikeService.execute(self.inputs)
        after_add_like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(initial_like_count + 1, after_add_like_count)

        self.assertEqual(UserHasLikedPostService.execute(self.inputs), True)

    def tearDown(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Like.objects.all().delete()
