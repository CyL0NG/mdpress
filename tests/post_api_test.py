#!/usr/bin/env python
# encoding: utf-8
import json
from unittest import TestCase

from application import create_app
import application.models as Models


class PostApiTest(TestCase):
    def setUp(self):
        self.app = create_app('TESTING')
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        Models.User(id=10000, username="zhangsan",
                    password="password",
                    email="liqianglau@outlook.com",
                    role=1).save()
        user = {
            'email': 'liqianglau@outlook.com',
            'password': 'password',
        }
        resp = self.client.post('/auth', data=json.dumps(user),
                                headers={'Content-Type': 'application/json'})
        login_resp = json.loads(resp.data)
        self.token = login_resp.get('access_token')

    def tearDown(self):
        for user in Models.User.objects.all():
            user.delete()
        for post in Models.Post.objects.all():
            post.delete()
        self.ctx.pop()

    def _add_a_post(self):
        post = {
            'title': 'title',
            'excerpt': 'excerpt',
            'content': 'content',
            'categories': [],
            'tags': [],
            'status': 1
        }
        self.client.post(
            '/posts/post', data=json.dumps(post),
            headers={'Authorization': 'JWT {}'.format(self.token),
                     'Content-Type': 'application/json'})

    def _get_all_post(self):
        return json.loads(self.client.get('/posts/all').data)['data']['posts']

    def test_add_post(self):
        post = {
            'title': 'title',
            'excerpt': 'excerpt',
            'content': 'content',
            'categories': [],
            'tags': [],
            'status': 1
        }
        resp = self.client.post(
            '/posts/post', data=json.dumps(post),
            headers={'Authorization': 'JWT {}'.format(self.token),
                     'Content-Type': 'application/json'})
        resp_data = json.loads(resp.data)
        resp_code = resp_data.get('code')
        resp_post = resp_data.get('data').get('post')
        self.assertEquals(resp_code, 2000)
        self.assertEquals(resp_post['title'], 'title')
        self.assertEquals(resp_code, 2000)

    def test_update_post(self):
        self._add_a_post()
        post = self._get_all_post()[0]
        post['title'] = 'new_title'
        resp = self.client.put(
            '/posts/post', data=json.dumps(post),
            headers={'Authorization': 'JWT {}'.format(self.token),
                     'Content-Type': 'application/json'})
        resp_data = json.loads(resp.data)
        resp_code = resp_data.get('code')
        resp_post = resp_data.get('data').get('post')
        self.assertEquals(resp_code, 2000)
        self.assertEquals(resp_post['title'], 'new_title')

    def test_delete_post(self):
        self._add_a_post()
        old_posts = self._get_all_post()
        post = old_posts[0]
        data = {'ids': [int(post.get('id'))]}
        print data
        resp = self.client.delete(
            '/posts/post', data=json.dumps(data),
            headers={'Authorization': 'JWT {}'.format(self.token),
                     'Content-Type': 'application/json'})
        resp_data = json.loads(resp.data)
        resp_code = resp_data.get('code')
        self.assertEquals(resp_code, 2000)
        new_posts = self._get_all_post()
        self.assertEquals(len(old_posts) - 1, len(new_posts))