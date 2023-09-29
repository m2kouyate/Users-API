from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserAPITestCase(APITestCase):
    """
    Тестовый случай для API пользователей.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_user(self):
        data = {"username": "newuser", "password": "newpassword", "password2": "newpassword", "email": "new@example.com", "first_name": "New", "last_name": "User"}
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_update_user(self):
        self.client.login(username="testuser", password="testpassword")
        data = {"first_name": "Updated"}
        response = self.client.patch(reverse('user-detail', args=[self.user.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_full_update_user(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "password": "updatedpassword",
            "password2": "updatedpassword",
            "first_name": "Updated",
            "last_name": "User"
        }
        response = self.client.put(reverse('user-detail', args=[self.user.id]), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_delete_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.delete(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_list_users(self):
        User.objects.create_user(username="testuser2", password="testpassword", email="test2@example.com")
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_registration(self):
        data = {
            "username": "registeruser",
            "password": "registerpassword",
            "password2": "registerpassword",
            "email": "register@example.com",
            "first_name": "Register",
            "last_name": "User"
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="registeruser").exists())
        self.assertIn('token', response.data)

    def test_sort_users(self):
        self.assertEqual(User.objects.count(), 1)
        User.objects.create_user(username="usera", first_name="Adam", email="adam@example.com")
        User.objects.create_user(username="userb", first_name="Eve", email="eve@example.com")
        response = self.client.get(reverse('user-list'), {'ordering': 'first_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[1]['first_name'], "Adam")
        self.assertEqual(response.data[2]['first_name'], "Eve")

    def test_filter_users(self):
        User.objects.create_user(username="userc", first_name="Charlie", email="charlie@example.com")
        User.objects.create_user(username="userd", first_name="David", email="david@example.com")
        response = self.client.get(reverse('user-list'), {'first_name': 'Charlie'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], "Charlie")



