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
from testsuite.nist.maurer_universal_statistical_test import MaurerUniversalTest
from testsuite.nist.approximate_entropy_test import ApproximateEntropyTest
from testsuite.nist.cumulative_sums_test import CumulativeSumsTest
from testsuite.nist.random_excursions_test import RandomExcursionsTest
from testsuite.nist.random_excursions_variant_test import RandomExcursionsVariantTest
from testsuite.test_utils.response import TestResponse
from testsuite.attack.berlekamp_massey import  BerlekampMassey


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
    'overlapping_template_matching': OverlappingTemplateMatchingTest.run_test,
    'maurer': MaurerUniversalTest.run_test,
    'entropy': ApproximateEntropyTest.run_test,
    'cusum': CumulativeSumsTest.run_test,
    'random_excursion': RandomExcursionsTest.run_test,
    'random_excursion_variant': RandomExcursionsVariantTest.run_test,
    'belkamp_massey': BerlekampMassey.run_test
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


from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from django.http import JsonResponse


def run_tests_parallel(test_list, bit_sequence, max_workers=None):
    """
    Exécute les tests en parallèle avec des processus séparés

    Args:
        test_list: Liste des noms de tests à exécuter
        bit_sequence: Séquence de bits à tester
        max_workers: Nombre maximum de processus (None = auto)
    """
    if max_workers is None:
        # Utiliser le nombre de CPU disponibles, mais limiter à 8 max
        max_workers = min(multiprocessing.cpu_count(), len(test_list), 8)

    test_results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Soumettre tous les tests
        future_to_test = {
            executor.submit(run_test, test_name, bit_sequence): test_name
            for test_name in test_list
        }

        # Collecter les résultats au fur et à mesure
        for future in as_completed(future_to_test):
            test_name = future_to_test[future]
            try:
                result = future.result()
                test_results.append(result)
            except Exception as exc:
                # Logger l'erreur
                import logging
                logging.error(f'Test {test_name} failed: {exc}')
                # Ajouter un résultat d'erreur
                test_results.append({
                    'test_name': test_name,
                    'error': True,
                    'error_message': str(exc)
                })

    return {
        "results": test_results,
        "count": len(test_results),
        "sequence_length": len(bit_sequence),
    }