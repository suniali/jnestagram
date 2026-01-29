from django.test import TestCase,Client

from django.contrib.auth import get_user_model
from django.urls import reverse

from django.core import mail

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from profiles.models import Country,Profile
from posts.models import Post,Tag,Comment,Replay,Like
from jnestagram.tokens import generate_token

User = get_user_model()

class RegisterViewTest(TestCase):
    def setUp(self):
        self.url=reverse('register')
        self.user_data={
            'username':'test',
            'email':'test@test.com',
            'password1':'testpassword',
            'password2':'testpassword'
        }

    def test_register_page_get(self):
        # request
        response=self.client.get(self.url)
        # check register page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/register.html')

    def test_register_success_logic(self):
        # Send form data
        response=self.client.post(self.url,self.user_data)
        # Check database for new user
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())
        user=User.objects.get(username=self.user_data['username'])
        # Check verify page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/verify_sent.html')
        # Check If Email Sent
        self.assertEqual(len(mail.outbox),1)
        sent_mail=mail.outbox[0]
        self.assertEqual(sent_mail.subject,'Activate your Account')
        self.assertEqual(sent_mail.to,[self.user_data['email']])
        # Check uid in mail body
        uid=urlsafe_base64_encode(force_bytes(user.pk))
        self.assertIn(uid,sent_mail.body)

    def test_authenticate_user_redirect(self):
        # Create and Login User
        user=User.objects.create(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password1'])
        user.profile.verified=True
        self.client.force_login(user)

        response=self.client.get(self.url)
        # Check loggined user should be redirect
        self.assertRedirects(response,reverse('home'))

    def test_invalid_registeration(self):
        bad_data=self.user_data.copy()
        bad_data['password2']='wrongpasswordmatches'

        response=self.client.post(self.url,bad_data)
        # User should not exist
        self.assertFalse(User.objects.filter(username=bad_data['username']).exists())
        # Register page should be show
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/register.html')

class ActiveViewTest(TestCase):
    def setUp(self):
        # Create unverified user
        self.user=User.objects.create(username='test',email='test@test.com',password='userpassword')
        self.profile=Profile.objects.get(user=self.user)
        self.profile.verified=False
        self.profile.save()

        # Create token and uid for user
        self.uid=urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token=generate_token.make_token(self.user)

        # create url
        self.url=reverse('activate',kwargs={'uidb64':self.uid,'token':self.token})

    def test_activation_success(self):
        response=self.client.get(self.url)

        # Check render page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/activation_success.html')

        # Check verified on Database
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.verified)

    def test_activation_invalid_token(self):
        invalid_url=reverse('activate',kwargs={'uidb64':self.uid,'token':'wrongtoken'})
        response=self.client.get(invalid_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/activation_invalid.html')

        # Check database should not change
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.verified)

    def test_activation_invalid_uidb64(self):
        invalid_url=reverse('activate',kwargs={'uidb64':'wronguidb64','token':self.token})
        response=self.client.get(invalid_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/activation_invalid.html')

        # Check database should not change
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.verified)

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
