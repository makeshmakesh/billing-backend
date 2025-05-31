# pylint:disable=all
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Plan, Subscription, Invoice

User = get_user_model()


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("user-list")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
        }
        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="existingpass123",
        )

    def test_user_registration_successful(self):
        """Anyone should be able to register a user."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="testuser").exists(), True)

    def test_user_list_requires_authentication(self):
        """Unauthenticated request to list users should be denied."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_user_list(self):
        """Authenticated user should be able to view user list."""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_user_creation_with_invalid_data(self):
        """Invalid registration data should return 400."""
        response = self.client.post(self.register_url, {"username": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PlanViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )

        self.plan_list_url = reverse("plan-list")  # assuming router basename is "plan"

        self.plan_data = {"name": "basic", "price": 499}

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_admin_can_list_plans(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.get(self.plan_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_plan(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.post(self.plan_list_url, self.plan_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plan.objects.count(), 1)

    def test_normal_user_can_access_plans(self):
        token = self.get_token_for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.get(self.plan_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_access_plans(self):
        response = self.client.get(self.plan_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username="user", password="userpass"
        )
        self.plan = Plan.objects.create(
            name="basic",
            price=100,
        )

        self.subscription_list_url = reverse("subscription-list")  # /subscriptions/
        self.create_data = {
            "start_date": "2025-05-31",
            "end_date": "2025-06-29",
            "plan": self.plan.id,
        }

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_user_can_create_subscription(self):
        self.authenticate(self.normal_user)
        response = self.client.post(
            self.subscription_list_url, self.create_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)

    def test_user_cannot_create_multiple_active_subscriptions(self):
        self.authenticate(self.normal_user)
        Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )

        response = self.client.post(
            self.subscription_list_url, self.create_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already have an active subscription", str(response.data))

    def test_user_can_view_their_own_subscriptions(self):
        sub = Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
        self.authenticate(self.normal_user)

        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], sub.id)

    def test_admin_can_view_all_subscriptions(self):
        Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
        self.authenticate(self.admin_user)

        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_user_cannot_access_subscriptions(self):
        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_soft_cancel_subscription_with_delete(self):
        sub = Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
        self.authenticate(self.normal_user)

        url = reverse("subscription-detail", kwargs={"pk": sub.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.status, "cancelled")

    def test_user_can_cancel_subscription_via_unsubscribe_action(self):
        sub = Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
        self.authenticate(self.normal_user)

        url = reverse(
            "subscription-unsubscribe", kwargs={"pk": sub.id}
        )  # /subscriptions/<id>/unsubscribe/
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.status, "cancelled")

    def test_cannot_cancel_already_cancelled_subscription(self):
        sub = Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            status="cancelled",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
        )
        self.authenticate(self.normal_user)

        url = reverse("subscription-unsubscribe", kwargs={"pk": sub.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already cancelled", str(response.data))


class InvoiceViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", password="adminpass", is_staff=True)
        self.normal_user = User.objects.create_user(username="user", password="userpass")

        self.plan = Plan.objects.create(name="basic", price=100, description="Basic plan")

        self.subscription = Subscription.objects.create(
            user=self.normal_user,
            plan=self.plan,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            status="active"
        )

        self.invoice = Invoice.objects.create(
            user=self.normal_user,
            subscription=self.subscription,
            plan=self.plan,
            amount=100,
            issue_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=7)).date(),
            status="pending"
        )

        self.invoice_url = reverse("invoice-list")

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_user_can_view_own_invoice(self):
        self.authenticate(self.normal_user)
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.invoice.id)

    def test_user_can_filter_invoices_by_status(self):
        self.authenticate(self.normal_user)
        response = self.client.get(self.invoice_url + "?status=pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_admin_can_view_all_invoices(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # def test_user_can_pay_invoice(self):
    #     self.authenticate(self.normal_user)
    #     url = reverse("invoice-pay", kwargs={"pk": self.invoice.id})
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["detail"], "Payment successful.")

    #     self.invoice.refresh_from_db()
    #     self.assertEqual(self.invoice.status, "paid")

    # def test_user_cannot_pay_already_paid_invoice(self):
    #     self.invoice.status = "paid"
    #     self.invoice.save()

    #     self.authenticate(self.normal_user)
    #     url = reverse("invoice-pay", kwargs={"pk": self.invoice.id})
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("already paid", response.data["detail"])

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)