from django.test import TestCase,Client

from django.contrib.auth import get_user_model
from django.urls import reverse

from profiles.models import Country
from posts.models import Post,Tag,Comment,Replay,Like

User = get_user_model()

class ProfileViewTest(TestCase):
    def setUp(self):
        username='test'
        email='test@test.com'
        username2='test2'
        email2='test2@test.com'
        password='testpassword'

        # Create New User
        self.user=User.objects.create_user(username=username, email=email, password=password)
        self.user2=User.objects.create_user(username=username2, email=email2, password=password)
        self.client=Client()
        self.client.login(username=username, password=password)
        self.url=reverse('profile')

        self.country=Country.objects.create(name='Iran',abbr='IR')
        tag=Tag.objects.create(name='TestTag',slug='testtag')
        post=Post.objects.create(user=self.user,title='Post 1')
        post.tag.set([tag])

    def test_profile_view_get_success(self):
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertIn('profile',response.context)
        self.assertEqual(response.context['posts_count'], 1)
        self.assertContains(response,'Iran')

    def test_profile_update_bio_and_phone(self):
        payload={
            'bio':'new test bio',
            'phone_number':'09121231213',
            'email':'test@test.com'
        }
        response=self.client.post(self.url,payload)

        self.assertRedirects(response,self.url)

        # Refresh Data
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio,payload['bio'])
        self.assertEqual(str(self.user.profile.phone_number),'9121231213')

    def test_profile_email_duplicate_error(self):
        old_email='test@test.com'
        exist_email='exsist@test.com'
        User.objects.create_user(username='test1', email=exist_email, password='testpassword')

        payload={
            'email':exist_email,
            'bio':'same bio'
        }
        response=self.client.post(self.url,payload)

        self.assertRedirects(response,self.url)

        messages=list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]),'This email is already in use.')

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.email,old_email)

    def test_unauthenticated_user(self):
        self.client.logout()
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/',response.url)
