from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Post


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='Test body content',
            status=Post.Status.PUBLISHED
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.author, self.user)

    def test_post_status_default_is_draft(self):
        draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            body='Draft body'
        )
        self.assertEqual(draft_post.status, Post.Status.DRAFT)

    def test_published_manager_returns_only_published(self):
        Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            body='Draft body',
            status=Post.Status.DRAFT
        )
        published_posts = Post.published.all()
        self.assertEqual(published_posts.count(), 1)
        self.assertEqual(published_posts.first(), self.post)

    def test_post_str(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_post_ordering(self):
        post2 = Post.objects.create(
            title='Second Post',
            slug='second-post',
            author=self.user,
            body='Second body',
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )
        posts = Post.published.all()
        self.assertEqual(posts.first(), post2)


class PostViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='Test body content',
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'])

    def test_post_list_does_not_show_drafts(self):
        Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            body='Draft body',
            status=Post.Status.DRAFT
        )
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        for post in response.context['posts']:
            self.assertEqual(post.status, Post.Status.PUBLISHED)

    def test_post_detail_view(self):
        response = self.client.get(
            reverse('blog:post_detail', args=[
                self.post.publish.year,
                self.post.publish.month,
                self.post.publish.day,
                self.post.slug
            ])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)

    def test_post_detail_404_for_draft(self):
        draft = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            body='Draft body',
            status=Post.Status.DRAFT,
            publish=timezone.now()
        )
        response = self.client.get(
            reverse('blog:post_detail', args=[
                draft.publish.year,
                draft.publish.month,
                draft.publish.day,
                draft.slug
            ])
        )
        self.assertEqual(response.status_code, 404)

    def test_post_share_get(self):
        response = self.client.get(
            reverse('blog:post_share', args=[self.post.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['sent'])

    def test_post_share_post_invalid_form(self):
        response = self.client.post(
            reverse('blog:post_share', args=[self.post.id]),
            {'name': '', 'email': 'bad-email', 'to': '', 'comments': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['sent'])

    def test_post_share_requires_published_post(self):
        draft = Post.objects.create(
            title='Draft',
            slug='draft',
            author=self.user,
            body='body',
            status=Post.Status.DRAFT,
            publish=timezone.now()
        )
        response = self.client.get(
            reverse('blog:post_share', args=[draft.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_post_list_by_tag(self):
        self.post.tags.add('django')
        response = self.client.get(
            reverse('blog:post_list_by_tag', args=['django'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'])

    def test_post_comment_requires_post(self):
        response = self.client.post(
            reverse('blog:post_comment', args=[self.post.id]),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'body': 'Great post!'
            }
        )
        # должен редиректить или возвращать 200
        self.assertIn(response.status_code, [200, 302])

    def test_post_comment_only_post_method(self):
        response = self.client.get(
            reverse('blog:post_comment', args=[self.post.id])
        )
        self.assertEqual(response.status_code, 405)
