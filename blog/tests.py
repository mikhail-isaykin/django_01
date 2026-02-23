from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


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
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
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

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertIn(self.post.slug, url)

    def test_post_has_body(self):
        self.assertEqual(self.post.body, 'Test body content')

    def test_post_publish_field(self):
        self.assertIsNotNone(self.post.publish)

    def test_post_created_auto(self):
        self.assertIsNotNone(self.post.created)

    def test_post_updated_auto(self):
        self.assertIsNotNone(self.post.updated)


class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='Test body',
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )
        self.comment = Comment.objects.create(
            post=self.post,
            name='John',
            email='john@example.com',
            body='Nice post!'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.name, 'John')
        self.assertEqual(self.comment.post, self.post)

    def test_comment_str(self):
        self.assertIn('John', str(self.comment))
        self.assertIn(str(self.post), str(self.comment))

    def test_comment_default_active(self):
        self.assertTrue(self.comment.active)

    def test_inactive_comment(self):
        self.comment.active = False
        self.comment.save()
        self.assertFalse(self.comment.active)

    def test_comment_related_to_post(self):
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first(), self.comment)

    def test_comment_ordering(self):
        Comment.objects.create(
            post=self.post,
            name='Alice',
            email='alice@example.com',
            body='Me too!'
        )
        comments = self.post.comments.all()
        self.assertEqual(comments.first(), self.comment)

    def test_multiple_comments_on_post(self):
        Comment.objects.create(
            post=self.post,
            name='Alice',
            email='alice@example.com',
            body='Second comment'
        )
        self.assertEqual(self.post.comments.count(), 2)

    def test_comment_email_field(self):
        self.assertEqual(self.comment.email, 'john@example.com')


class EmailPostFormTest(TestCase):

    def test_valid_form(self):
        form = EmailPostForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'to': 'friend@example.com',
            'comments': 'Check this out!'
        })
        self.assertTrue(form.is_valid())

    def test_valid_form_without_comments(self):
        form = EmailPostForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'to': 'friend@example.com',
            'comments': ''
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = EmailPostForm(data={
            'name': 'John',
            'email': 'not-an-email',
            'to': 'friend@example.com',
            'comments': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_to_email(self):
        form = EmailPostForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'to': 'not-an-email',
            'comments': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('to', form.errors)

    def test_missing_required_fields(self):
        form = EmailPostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('to', form.errors)

    def test_name_max_length(self):
        form = EmailPostForm(data={
            'name': 'J' * 26,
            'email': 'john@example.com',
            'to': 'friend@example.com',
            'comments': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_comments_not_required(self):
        form = EmailPostForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'to': 'friend@example.com',
        })
        self.assertTrue(form.is_valid())


class CommentFormTest(TestCase):

    def test_valid_form(self):
        form = CommentForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'body': 'Great post!'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = CommentForm(data={
            'name': 'John',
            'email': 'bad-email',
            'body': 'Great post!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_missing_required_fields(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('body', form.errors)

    def test_form_fields(self):
        form = CommentForm()
        self.assertEqual(list(form.fields.keys()), ['name', 'email', 'body'])

    def test_empty_body_invalid(self):
        form = CommentForm(data={
            'name': 'John',
            'email': 'john@example.com',
            'body': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


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

    def test_post_list_by_tag_not_found(self):
        response = self.client.get(
            reverse('blog:post_list_by_tag', args=['nonexistent-tag'])
        )
        self.assertEqual(response.status_code, 404)

    def test_post_comment_only_post_method(self):
        response = self.client.get(
            reverse('blog:post_comment', args=[self.post.id])
        )
        self.assertEqual(response.status_code, 405)

    def test_post_comment_creates_comment(self):
        self.client.post(
            reverse('blog:post_comment', args=[self.post.id]),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'body': 'Great post!'
            }
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.name, 'Test User')
        self.assertTrue(comment.active)

    def test_post_detail_has_comments_in_context(self):
        Comment.objects.create(
            post=self.post,
            name='John',
            email='john@example.com',
            body='Nice!'
        )
        response = self.client.get(
            reverse('blog:post_detail', args=[
                self.post.publish.year,
                self.post.publish.month,
                self.post.publish.day,
                self.post.slug
            ])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
