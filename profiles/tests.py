from django.test import TestCase,Client

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

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

class ComplateProfileViewTest(TestCase):
    def setUp(self):
        self.user=User.objects.create(username='test',email='test@test.com',password='userpassword')
        self.country=Country.objects.create(name='Iran',abbr='IR')
        self.url=reverse('complate_profile')

    def test_profile_created_after_user_created(self):
        # check profile created by signal
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_context_data_contains_countries(self):
        self.client.force_login(self.user)

        responses=self.client.get(self.url)

        self.assertIn('countries',responses.context)
        self.assertTrue(responses.context['countries'].filter(name='Iran').exists())

    def test_login_required(self):
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/',response.url)

    def test_update_profile_success(self):
        self.client.force_login(self.user)

        form_data={
            'bio':'I am Trader.',
            'country':self.country.id,
            'phone_number':'09121231231',
        }

        response=self.client.post(self.url,data=form_data)
        # check redirect
        self.assertRedirects(response,reverse('profile'))

        # Check profile database for new datas
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio,form_data['bio'])
        self.assertEqual(self.user.profile.country,self.country)
        self.assertEqual(str(self.user.profile.phone_number),'9121231231')


        # Check Messages
        messages=list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(str(messages[0]),'Your profile has been updated.')

class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.url=reverse('login')
        self.password='userpassword'

        # Create Verified User
        self.verified_user = User.objects.create_user(username='verified', password=self.password)
        self.verified_user.profile.verified = True
        self.verified_user.profile.save()

        # ساخت کاربر وریفای نشده
        self.unverified_user = User.objects.create_user(username='unverified', password=self.password)
        self.unverified_user.profile.verified = False
        self.unverified_user.profile.save()

    def test_login_get_success(self):
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/login.html')


    def test_login_seccess_verified_user(self):
        response=self.client.post(self.url,data={
            'username':self.verified_user.username,
            'password':self.password
        })
        self.assertRedirects(response,reverse('home'))
        # Check setiton
        self.assertIn('_auth_user_id',self.client.session)

    def test_login_fail_unverified_user(self):
        response=self.client.post(self.url,data={
            'username':self.unverified_user.username,
            'password':self.password
        })
        # Check redirect
        self.assertRedirects(response,self.url)

        # Check warning message
        messages=list(get_messages(response.wsgi_request))
        self.assertTrue(any('Your account is not verified' in m.message for m in messages))

        # Check sesstion
        self.assertNotIn('_auth_user_id',self.client.session)

    def test_login_invalid_credentials(self):
        response=self.client.post(self.url,data={
            'username':self.verified_user.username,
            'password':'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        messages=list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid credentials' in m.message for m in messages))

    def test_redirect_already_authenticated_user(self):
        self.client.force_login(self.verified_user)
        response=self.client.get(self.url)

        self.assertRedirects(response,reverse('home'))

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

class PublicProfileViewTest(TestCase):
    def setUp(self):
        # Create User
        self.user=User.objects.create_user(username='test_user', password='testpassword')
        self.profile=self.user.profile
        self.profile.verified=True
        self.profile.save()

        # Create Post
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )
        self.fake_image = SimpleUploadedFile('test_image.gif', small_gif, content_type='image/gif')
        self.post=Post.objects.create(user=self.user,title='Post Test',text='Text Test',image=self.fake_image)

        # Create Visitor User
        self.visitor=User.objects.create_user(username='visitor', password='testpassword')
        self.visitor.profile.verified=True
        self.visitor.profile.save()

        self.url=reverse('public_profile',kwargs={'username':self.user.username})

    def test_public_profile_basic_load(self):
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/public_profile.html')
        self.assertContains(response,'test_user')
        self.assertIn('posts',response.context)
        self.assertEqual(len(response.context['posts']),1)

    def test_annotate_likes_for_authenticate_user(self):
        content_type=ContentType.objects.get_for_model(Post)
        Like.objects.create(user=self.visitor,content_type=content_type,object_id=str(self.post.id))

        self.client.force_login(self.visitor)
        response=self.client.get(self.url)

        post_in_context=response.context['posts'][0]
        self.assertTrue(post_in_context.is_liked)

    def test_htmx_posts_request(self):
        response=self.client.get(self.url,HTTP_HX_REQUEST='true')

        # Should render post container
        self.assertTemplateUsed(response,'partials/posts/posts_container.html')
        self.assertTemplateNotUsed(response,'profiles/profile.html')

    def test_top_posts_query_param(self):
        top_post=Post.objects.create(user=self.user,title='Top Post',text='Top Post',likes_count=10,image=self.fake_image)

        response=self.client.get(self.url+'?top-posts')

        posts=response.context['posts']
        self.assertEqual(posts[0],top_post)
        self.assertTrue(all(p.likes_count > 0 for p in posts))

    def test_htmx_top_posts_request(self):
        response=self.client.get(self.url+'?top-posts',HTTP_HX_REQUEST='true')

        self.assertTemplateUsed(response,'partials/posts/posts_container.html')
        self.assertTemplateNotUsed(response,'profiles/profile.html')
        self.assertIn('posts',response.context)

    def test_unauthenticated_user_is_like_is_false(self):
        response=self.client.get(self.url)

        post_in_context=response.context['posts'][0]
        self.assertFalse(post_in_context.is_liked)

    def test_top_comments_logic_and_prefetch(self):
        top_post = Post.objects.create(
            user=self.user,
            title='Top Post',
            text='Top Post',
            likes_count=10,
            image=self.fake_image
        )
        top_comment=Comment.objects.create(
            user=self.user,
            post=top_post,
            text='Top Comment',
            is_approved=True,
            likes_count=5,
        )

        # Create unaccept comments(not approved,without likes)
        Comment.objects.create(user=self.user,post=top_post,text="Hidden",is_approved=False,likes_count=10)
        Comment.objects.create(user=self.user,post=top_post,text="No Likes",is_approved=True,likes_count=0)

        # Create Replay for top comment
        replay=Replay.objects.create(user=self.visitor,comment=top_comment,text='I am a replay')

        response=self.client.get(self.url+'?top-comments')

        self.assertIn('top_comments',response.context)
        self.assertEqual(len(response.context['top_comments']),1)
        self.assertEqual(response.context['top_comments'][0],top_comment)

        comment_in_context=response.context['top_comments'][0]
        self.assertTrue(hasattr(comment_in_context,'replies'))
        self.assertEqual(comment_in_context.replies[0],replay)

    def test_htmx_top_comments_request(self):
        response=self.client.get(self.url+'?top-comments',HTTP_HX_REQUEST='true')

        self.assertTemplateUsed(response,'partials/posts/comments_container.html')
        self.assertIn('display_comments',response.context)

class UserDeleteViewTest(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='victim', password='testpassword')
        self.attaker=User.objects.create_user(username='attaker', password='testpassword')
        self.url=reverse('delete_profile',kwargs={'pk':self.user.id})


    def test_delete_context_data(self):
        self.client.force_login(self.user)
        response=self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'layouts/generic_delete.html')
        self.assertTrue(hasattr(response,'context'))
        self.assertEqual(response.context['object_type'],f'User : {self.user.username}')
        self.assertEqual(response.context['cancel_url'],reverse('profile'))

    def test_only_owner_can_delete_account(self):
        self.client.force_login(self.attaker)
        response=self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_soft_delete_logic(self):
        self.client.force_login(self.user)

        response=self.client.post(self.url)

        # Check redirect to home
        self.assertRedirects(response,reverse('home'))

        # Check soft delete on database
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # Check session
        self.assertNotIn('_auth_user_id',self.client.session)
        # Check messages
        messages=list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),'Your account has been deleted.')

class ApprovedCommentTest(TestCase):
    def setUp(self):
        # Owner
        self.owner=User.objects.create_user(username='owner', password='testpassword')
        # Stranger
        self.stranger=User.objects.create_user(username='stranger', password='testpassword')

        # Create a post for Owner
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )
        self.fake_image=SimpleUploadedFile('test_image.gif',small_gif,content_type='image/gif')
        self.post=Post.objects.create(
            user=self.owner,
            title='Post 1',
            text='Post Text',
            image=self.fake_image
        )

        # UnApproved Comment for post
        self.comment=Comment.objects.create(
            user=self.stranger,
            post=self.post,
            text='Nice Post!',
            is_approved=False
        )

        self.url=reverse('approve_comment',kwargs={'pk':self.comment.id})

    def test_login_required_to_approve(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/',response.url)


    def test_approve_comment_success(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)

        # Check redirect
        self.assertRedirects(response,reverse('profile'))

        # Check Database for comment has been approved
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_approved)
        # Check messages
        messages=list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),'Comment has been approved and is now public.')

    def test_stranger_can_not_approve_comment(self):
        self.client.force_login(self.stranger)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

        # Check database for comment should not be approve
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_approved)
