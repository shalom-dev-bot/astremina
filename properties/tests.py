from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from properties.models import Property, Favorite
from datetime import datetime

User = get_user_model()

class PropertyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@astremina.com',
            password='test123',
            first_name='Test',
            last_name='User'
        )
        self.property = Property.objects.create(
            title='Test House',
            slug='test-house',
            description='A test house',
            property_type='house',
            price=1000000,
            currency='XAF',
            city='Douala',
            owner=self.user,
            status='published'
        )

    def test_property_str(self):
        self.assertEqual(str(self.property), 'Test House')

    def test_property_slug_auto(self):
        self.assertEqual(self.property.slug, 'test-house')

    def test_property_status(self):
        self.assertEqual(self.property.status, 'published')

class PropertyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@astremina.com',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(
            title='Test House',
            slug='test-house',
            description='A test house',
            property_type='house',
            price=1000000,
            currency='XAF',
            city='Douala',
            owner=self.user,
            status='published'
        )

    def test_property_list(self):
        response = self.client.get(reverse('properties:list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Test House')

    def test_property_detail(self):
        response = self.client.get(reverse('properties:detail', kwargs={'slug': 'test-house'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Test House')

    def test_property_create_authenticated(self):
        data = {
            'title': 'New House',
            'description': 'A new house',
            'property_type': 'house',
            'price': 2000000,
            'currency': 'XAF',
            'city': 'Yaoundé'
        }
        response = self.client.post(reverse('api:property-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 2)
        self.assertEqual(Property.objects.last().title, 'New House')

class FavoriteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@astremina.com',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(
            title='Test House',
            slug='test-house',
            description='A test house',
            property_type='house',
            price=1000000,
            currency='XAF',
            city='Douala',
            owner=self.user,
            status='published'
        )

    def test_add_favorite(self):
        response = self.client.post(
            reverse('api:favorite-list'),
            {'property_id': str(self.property.id)},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(Favorite.objects.first().property.title, 'Test House')

    def test_add_duplicate_favorite(self):
        Favorite.objects.create(user=self.user, property=self.property)
        response = self.client.post(
            reverse('api:favorite-list'),
            {'property_id': str(self.property.id)},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_remove_favorite(self):
        favorite = Favorite.objects.create(user=self.user, property=self.property)
        response = self.client.delete(reverse('api:favorite-remove', kwargs={'pk': favorite.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Favorite.objects.count(), 0)
        self.assertContains(response, 'Favorite removed')

    def test_favorite_list(self):
        Favorite.objects.create(user=self.user, property=self.property)
        response = self.client.get(reverse('api:favorite-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Test House')