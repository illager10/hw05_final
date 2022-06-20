from ..forms import PostForm
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
import tempfile
import shutil


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description'
        )
        cls.form = PostForm()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='test_username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_entry(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test_text_2',
            'group': 1,
            'image': self.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'test_username'})
                             )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, 'test_text_2')
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_post_entry_can_be_edited(self):
        """Запись в Post редактируется"""
        Post.objects.create(author=self.user)
        form_data = {
            'text': 'modified_text',
            'group': 1,
            'id': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, 'modified_text')
        self.assertEqual(post.group, self.group)
        self.assertEqual(Post.objects.first().pub_date.date(),
                         timezone.now().date()
                         )
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_cannot_create_post(self):
        """ Неавторизованный пользователь не может создавать посты """
        guest_client = Client()
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test_text_2',
            'group': 1,
        }
        response = guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
