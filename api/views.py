from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import TestSuite, TestCase
from api.serializers import TestSuiteSerializer, TestCaseSerializer
from testsuite.config import run_test, run_tests_parallel
from rest_framework.parsers import MultiPartParser, JSONParser
import json
from django.conf import settings
import time
from rest_framework.permissions import IsAuthenticated





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

class TestResult(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            start_time = time.time()

            # --- Lecture et parsing de test_list ---
            raw_test_list = request.data.get("test_list")
            if isinstance(raw_test_list, str):
                test_list = json.loads(raw_test_list)
            elif isinstance(raw_test_list, list):
                test_list = raw_test_list
            else:
                raise ValueError("Le champ 'test_list' est requis et doit être une liste.")

            if not test_list:
                raise ValueError("La liste de tests ne peut pas être vide.")

            # --- Lecture de la séquence ---
            bit_sequence = []

            if "bit_file" in request.FILES:
                bit_file = request.FILES["bit_file"]
                file_content = bit_file.read().decode("utf-8")
                bit_sequence = [int(b) for b in file_content.strip() if b in "01"]
            elif "bit_sequence" in request.data:
                bit_sequence = request.data["bit_sequence"]
                if isinstance(bit_sequence, str):
                    bit_sequence = [int(b) for b in bit_sequence.strip() if b in "01"]
            else:
                raise ValueError("Veuillez fournir un fichier ou une séquence de bits ('bit_file' ou 'bit_sequence').")

            # --- Exécution des tests ---
            test_results = []
            for test_name in test_list:
                test_result = run_test(test_name, bit_sequence)
                test_results.append(test_result)

            duration = time.time() - start_time

            # --- Récupération des informations utilisateur ---
            user = request.user
            user_info = {
                "id": user.id,
                "username": user.username if user.username else None,
                "first_name": user.first_name if user.first_name else None,
                "last_name": user.last_name if user.last_name else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }

            return Response({
                "results": test_results,
                "count": len(test_results),
                "sequence_length": len(bit_sequence),
                "duration": self._format_time(duration),
                "user_info": user_info
            })

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": f"Erreur lors de l'exécution des tests: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _format_time(seconds):
        """
        Formate le temps en secondes vers un format lisible

        Args:
            seconds (float): Temps en secondes

        Returns:
            str: Temps formaté (ex: "1.234s", "567ms", "2m 30s")
        """
        if seconds < 0.001:
            return f"{seconds * 1000000:.0f}μs"
        elif seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.3f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            remaining_seconds = seconds % 60
            return f"{hours}h {minutes}m {remaining_seconds:.1f}s"