from django.test import TestCase, Client
from django.urls import reverse

class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page_loads(self):
        """Test that the index page loads successfully"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html') 