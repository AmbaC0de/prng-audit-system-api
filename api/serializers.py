from rest_framework import serializers
from api.models import TestSuite, TestCase


class TestSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'description']


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'key', 'name', 'description', 'test_suite']
