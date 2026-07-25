from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Newspaper, Topic


class ModelsTests(TestCase):
    def test_topic_str(self):
        topic = Topic.objects.create(name="Politics")
        self.assertEqual(str(topic), "Politics")

    def test_redactor_str(self):
        redactor = get_user_model().objects.create_user(
            username="john",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(str(redactor), "john (John Doe)")

    def test_newspaper_str(self):
        topic = Topic.objects.create(name="Weather")
        newspaper = Newspaper.objects.create(
            title="Sunny days ahead",
            content="Weather report",
            published_date="2026-07-25",
            topic=topic,
        )
        self.assertEqual(str(newspaper), "Sunny days ahead")


class PublicAccessTests(TestCase):
    """Anonymous users must be redirected to login for any page."""

    def test_index_login_required(self):
        response = self.client.get(reverse("news:index"))
        self.assertNotEqual(response.status_code, 200)

    def test_topic_list_login_required(self):
        response = self.client.get(reverse("news:topic-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_newspaper_list_login_required(self):
        response = self.client.get(reverse("news:newspaper-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_redactor_list_login_required(self):
        response = self.client.get(reverse("news:redactor-list"))
        self.assertNotEqual(response.status_code, 200)


class RegularUserPermissionTests(TestCase):
    """Logged-in but non-staff users can view, but not modify data."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="regular_user",
            password="testpass123",
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Crime")

    def test_can_view_topic_list(self):
        response = self.client.get(reverse("news:topic-list"))
        self.assertEqual(response.status_code, 200)

    def test_can_view_newspaper_list(self):
        response = self.client.get(reverse("news:newspaper-list"))
        self.assertEqual(response.status_code, 200)

    def test_cannot_create_topic(self):
        response = self.client.get(reverse("news:topic-create"))
        self.assertEqual(response.status_code, 403)

    def test_cannot_update_topic(self):
        response = self.client.get(
            reverse("news:topic-update", kwargs={"pk": self.topic.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_cannot_delete_topic(self):
        response = self.client.get(
            reverse("news:topic-delete", kwargs={"pk": self.topic.pk})
        )
        self.assertEqual(response.status_code, 403)


class StaffUserPermissionTests(TestCase):
    """Staff (redactor) users can create, update, and delete data."""

    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="staff_user",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_can_create_topic(self):
        response = self.client.post(
            reverse("news:topic-create"),
            {"name": "Sport"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Topic.objects.filter(name="Sport").exists())

    def test_can_update_topic(self):
        topic = Topic.objects.create(name="Old name")
        response = self.client.post(
            reverse("news:topic-update", kwargs={"pk": topic.pk}),
            {"name": "New name"},
        )
        self.assertEqual(response.status_code, 302)
        topic.refresh_from_db()
        self.assertEqual(topic.name, "New name")

    def test_can_delete_topic(self):
        topic = Topic.objects.create(name="Temporary")
        response = self.client.post(
            reverse("news:topic-delete", kwargs={"pk": topic.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Topic.objects.filter(pk=topic.pk).exists())


class SignUpTests(TestCase):
    def test_signup_creates_non_staff_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "new_reader",
                "first_name": "New",
                "last_name": "Reader",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new_reader")
        self.assertFalse(user.is_staff)


class NewspaperTopicFilterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reader",
            password="testpass123",
        )
        self.client.force_login(self.user)
        self.topic_a = Topic.objects.create(name="Art")
        self.topic_b = Topic.objects.create(name="Trade")
        Newspaper.objects.create(
            title="Art news",
            content="content",
            published_date="2026-07-25",
            topic=self.topic_a,
        )
        Newspaper.objects.create(
            title="Trade news",
            content="content",
            published_date="2026-07-25",
            topic=self.topic_b,
        )

    def test_filter_by_topic(self):
        response = self.client.get(
            reverse("news:newspaper-list"), {"topic": self.topic_a.pk}
        )
        titles = [n.title for n in response.context["newspaper_list"]]
        self.assertEqual(titles, ["Art news"])

    def test_no_filter_shows_all(self):
        response = self.client.get(reverse("news:newspaper-list"))
        titles = [n.title for n in response.context["newspaper_list"]]
        self.assertEqual(len(titles), 2)
