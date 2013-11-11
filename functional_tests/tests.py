"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from time import sleep
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore

from django.test import LiveServerTestCase, Client
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pypo import settings
import sys

EXAMPLE_COM = 'http://www.example.com/'


class PypoLiveServerTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = arg.split('=')[1]
                return
        LiveServerTestCase.setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            LiveServerTestCase.tearDownClass()



class ExistingUserTest(PypoLiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.b = webdriver.Firefox()
        self.b.implicitly_wait(3)
        self.c = Client()

    def tearDown(self):
        self.b.quit()

    def create_pre_authenticated_session(self):
        try:
            user = User.objects.get(username='uther')
        except User.DoesNotExist:
            user = User.objects.create(username='uther')
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## to set a cookie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.b.get(self.live_server_url + "/404_no_such_url/")
        self.b.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
            ))

    def _add_example_item(self):
        # Open the add item page
        self.b.get(self.live_server_url+'/add')

        # He submits a link
        input_url = self.b.find_element_by_name('url')
        input_url.send_keys(EXAMPLE_COM)
        input_url.send_keys(Keys.ENTER)

    def test_login_dev_user(self):
        self.b.get(self.server_url)

        # He sees the login form and sends it
        self.assertEqual('Username*', self.b.find_element_by_id('div_id_username').text,
                         'Login form not found')
        input_username = self.b.find_element_by_name('username')
        input_username.send_keys('dev')
        input_pass = self.b.find_element_by_name('password')
        input_pass.send_keys('dev')
        input_pass.send_keys(Keys.ENTER)

        # He can see the navigation bar
        self.assertIsNotNone(self.b.find_element_by_id('id_link_add'), 'Add item link not found')

    def test_can_add_an_item_and_see_it_in_the_list(self):
        self.create_pre_authenticated_session()

        # User opens pypo and has no items in his list
        self.b.get(self.live_server_url)
        self.assertEqual(0, len(self.b.find_elements_by_class_name('item')))

        # He opens the add item page and sees the form
        self.b.get(self.live_server_url+'/add')

        # He submits a link
        input_url = self.b.find_element_by_name('url')
        input_url.send_keys(EXAMPLE_COM)
        input_url.send_keys(Keys.ENTER)

        # The link is now in his list
        items = self.b.find_elements_by_class_name('item_link')
        self.assertEqual(1, len(items), 'Item was not added')
        self.assertEqual(EXAMPLE_COM, items[0].get_attribute('href'))

        # The domain is in the link text
        self.assertIn(u'[example.com]', items[0].text)

    def test_added_items_are_searchable(self):
        self.create_pre_authenticated_session()
        self._add_example_item()
        # Uther visits the search page and searches for the example page
        self.b.find_element_by_id('id_link_search').click()
        search_input = self.b.find_element_by_name('q')
        search_input.send_keys('example')
        search_input.send_keys(Keys.ENTER)

        # He sees the example item with a link pointing to example.com
        items = self.b.find_elements_by_class_name('item_link')
        self.assertEqual(1, len(items), 'Item not found in results')
        self.assertEqual(EXAMPLE_COM, items[0].get_attribute('href'))
        self.assertIn('[example.com]', items[0].text)

    def test_invalid_searches_return_no_results(self):
        self.create_pre_authenticated_session()
        self._add_example_item()
        # Uther visits the search page and searches for an unknown term
        self.b.find_element_by_id('id_link_search').click()
        search_input = self.b.find_element_by_name('q')
        search_input.send_keys('invalid_search')
        search_input.send_keys(Keys.ENTER)

        # He sees no results
        items = self.b.find_elements_by_class_name('item_link')
        self.assertEqual(0, len(items))
        self.assertIn('No results found.',
                            (p.text for p in self.b.find_elements_by_tag_name('p')))


