from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import TestSuite, TestCase
from api.serializers import TestSuiteSerializer, TestCaseSerializer
from testsuite.config import run_test
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser



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
    def post(self, request):
        try:
            # Convertir la séquence en liste d'entiers si elle est donnée comme chaîne
            bit_sequence = request.data['bit_sequence']
            if isinstance(request.data['bit_sequence'], str):
                bit_sequence = [int(bit) for bit in request.data['bit_sequence']]
            test_list = request.data['test_list']
            test_results = []
            for test_name in test_list:
                test_result = run_test(test_name, bit_sequence)
                test_results.append(test_result)
            return Response({
                "results": test_results,
                "count": len(test_results),
                "sequence_length": len(bit_sequence)
            }, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response({
                "error": f"Champ manquant: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": f"Erreur lors de l'exécution des tests: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class TestResult(APIView):
#     # parser_classes = [FormParser, MultiPartParser]
#
#     def post(self, request):
#         try:
#             bit_sequence = None
#             # Vérifier si un fichier est fourni
#             if 'bit_file' in request.data:
#                 bit_file = request.data['bit_file']
#                 try:
#                     # Lire le contenu du fichier
#                     file_content = bit_file.read().decode('utf-8').strip()
#                     # Convertir en liste d'entiers
#                     bit_sequence = [int(bit) for bit in file_content if bit in '01']
#                 except (UnicodeDecodeError, ValueError) as e:
#                     return Response({
#                         "error": f"Erreur lors de la lecture du fichier: {str(e)}"
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#             # Sinon, utiliser la séquence fournie directement
#             elif 'bit_sequence' in request.data:
#                 if isinstance(request.data['bit_sequence'], str):
#                     bit_sequence = [int(bit) for bit in request.data['bit_sequence']]
#                 else:
#                     bit_sequence = request.data['bit_sequence']
#
#             else:
#                 return Response({
#                     "error": "Veuillez fournir soit 'bit_sequence' soit 'bit_file'"
#                 }, status=status.HTTP_400_BAD_REQUEST)
#
#             # Vérifier que la séquence n'est pas vide
#             if not bit_sequence:
#                 return Response({
#                     "error": "La séquence de bits est vide"
#                 }, status=status.HTTP_400_BAD_REQUEST)
#
#             test_list = request.data['test_list']
#             test_results = []
#
#             for test_name in test_list:
#                 test_result = run_test(test_name, bit_sequence)
#                 test_results.append(test_result)
#
#             return Response({
#                 "results": test_results,
#                 "count": len(test_results),
#                 "sequence_length": len(bit_sequence)
#             }, status=status.HTTP_200_OK)
#
#         except KeyError as e:
#             return Response({
#                 "error": f"Champ manquant: {str(e)}"
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except ValueError as e:
#             return Response({
#                 "error": f"Erreur de format dans la séquence de bits: {str(e)}"
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 "error": f"Erreur lors de l'exécution des tests: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
