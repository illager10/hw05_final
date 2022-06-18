from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='test_usrneme')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='test_text',
            author=self.user,
            group=self.group,
            image=self.image,
        )

    def cache_index_test(self):
        Post.objects.create(author=self.user)
        Post.objects.filter(author=self.user).delete
        self.assertEqual(Post.objects.count(), 1)
        cache.clear()
        self.assertEqual(Post.objects.count(), 0)
