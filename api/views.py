from rest_framework import status, generics
from api.models import TestSuite, TestCase
from api.serializers import TestSuiteSerializer, TestCaseSerializer


# Create your views here.

class TestSuiteList(generics.ListCreateAPIView):
    """
    Liste toutes les batteries de test
    """
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializer


class TestSuiteDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a test suite.
    """
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializer


class TestCaseList(generics.ListCreateAPIView):
    """
    Liste des tests d'une batterie de test
    """
    serializer_class = TestCaseSerializer

    def get_queryset(self):
        """
        Cette méthode retourne uniquement les tests associés
        à la batterie de test spécifiée dans l'URL
        """
        test_suite_id = self.kwargs['pk']
        return TestCase.objects.filter(test_suite_id=test_suite_id)

class TestCaseDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TestCaseSerializer
    queryset = TestCase.objects.all()
