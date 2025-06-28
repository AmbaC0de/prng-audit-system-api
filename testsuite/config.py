from testsuite.nist.binary_matrix_rank_test import BinaryMatrixRankTest
from testsuite.nist.frequency_monobit_test import FrequencyMonobitTest
from testsuite.nist.frequency_test_within_a_block import FrequencyTestWithinABlock
from testsuite.nist.linear_complexity_test import LinearComplexityTest
from testsuite.nist.longest_run_of_one_in_a_block_test import LongestRunOfOneInABlockTest
from testsuite.nist.non_overlapping_template_matching_test import NonOverlappingTemplateMatchingTest
from testsuite.nist.runs_test import RunsTest
from testsuite.nist.serial_test import SerialTest
from testsuite.nist.discrete_fourier_transform_test import DiscreteFourierTransformTest
from testsuite.nist.overlapping_template_matching_test import OverlappingTemplateMatchingTest
from testsuite.test_utils.response import TestResponse


# Dictionnaire qui mappe les noms de tests aux fonctions correspondantes
TEST_FUNCTIONS = {
    'frequency_monobit': FrequencyMonobitTest.run_test,
    'block_frequency': FrequencyTestWithinABlock.run_test,
    'runs': RunsTest.run_test,
    'longest_runs': LongestRunOfOneInABlockTest.run_test,
    'non_overlapping_template_matching': NonOverlappingTemplateMatchingTest.run_test,
    'binary_matrix_rank': BinaryMatrixRankTest.run_test,
    'linear_complexity': LinearComplexityTest.run_test,
    'serial': SerialTest.run_test,
    'dft_spectral': DiscreteFourierTransformTest.run_test,
    'overlapping_template_matching': OverlappingTemplateMatchingTest.run_test
    # Ajoutez ici d'autres tests
}

def get_available_tests():
    """
    Renvoie la liste des tests disponibles
    """
    return list(TEST_FUNCTIONS.keys())

def run_test(test_name, bit_sequence, **kwargs):
    """
    Exécute un test spécifique

    Args:
        test_name (str): Nom du test à exécuter
        bit_sequence (list): Séquence de bits à tester
        **kwargs: Arguments supplémentaires à passer au test

    Returns:
        dict: Résultat du test
    """
    if test_name in TEST_FUNCTIONS:
        return TEST_FUNCTIONS[test_name](bit_sequence, **kwargs)
    else:
        response_handler = TestResponse('Test inconnu')
        return response_handler.get_response(
            error=True,
            error_message=f"Test '{test_name}' non reconnu"
        )
