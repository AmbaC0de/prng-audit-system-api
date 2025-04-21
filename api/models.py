from django.db import models
from django.utils import timezone

class TestSuite(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TestCase(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
