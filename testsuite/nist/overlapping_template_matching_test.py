from testsuite.test_utils.response import TestResponse
import math
import numpy as np
import scipy.special
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class OverlappingTemplateMatchingTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE, template=None):
        """
        Effectue le test de correspondance de template avec chevauchement selon la méthode NIST SP 800-22.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester
            decision_rule (float): Seuil de décision (par défaut: 0.01)
            template (list[int]): Template à rechercher (par défaut: [1,1,1,1,1,1,1,1,1] - 9 uns)

        Returns:
            dict: Résultats du test
        """
        response_handler = TestResponse('Test de correspondance de template avec chevauchement')

        try:
            n = len(bit_sequence)

            # Template par défaut : 9 uns consécutifs
            if template is None:
                template = [1] * 9

            m = len(template)  # Longueur du template

            # Vérifications préliminaires
            if n < 1000:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 1000 bits requis)"
                )

            if m >= 22:
                return response_handler.get_response(
                    error=True,
                    error_message="Le template est trop long (maximum 21 bits)"
                )

            # Paramètres pour le template de 9 bits (template par défaut)
            if m == 9 and template == [1] * 9:
                # Valeurs corrigées selon les recherches NIST
                K = 5  # Nombre de classes
                M = 1032  # Longueur de bloc
                N = n // M  # Nombre de blocs

                # Probabilités corrigées pour le template 111111111 (9 uns)
                pi = [0.364091, 0.185659, 0.139381, 0.100571, 0.0704323, 0.139865]

                # Valeurs lambda et eta pour le calcul
                lambda_val = (M - m + 1) / (2 ** m)  # Espérance
                eta = lambda_val / 2.0

            else:
                # Calcul générique pour d'autres templates
                M = 1032
                N = n // M
                K = 5

                # Probabilité d'occurrence du template
                template_prob = 1.0 / (2 ** m)
                lambda_val = (M - m + 1) * template_prob
                eta = lambda_val / 2.0

                # Calcul des probabilités approximatives (formule générique)
                pi = []
                for i in range(K):
                    if i < K - 1:
                        pi.append(math.exp(-eta) * (eta ** i) / math.factorial(i))
                    else:
                        pi.append(1 - sum(pi))

            if N == 0:
                return response_handler.get_response(
                    error=True,
                    error_message=f"Séquence trop courte pour créer des blocs de taille {M}"
                )

            # Compter les occurrences dans chaque bloc
            v = [0] * (K + 1)  # Compteurs pour chaque classe

            for i in range(N):
                # Extraire le bloc
                block_start = i * M
                block_end = min(block_start + M, n)
                block = bit_sequence[block_start:block_end]

                # Compter les occurrences chevauchantes du template dans ce bloc
                count = 0
                for j in range(len(block) - m + 1):
                    if block[j:j + m] == template:
                        count += 1

                # Classer le nombre d'occurrences
                if count <= K:
                    v[count] += 1
                else:
                    v[K] += 1  # Plus de K occurrences

            # Calcul de la statistique chi-carré
            chi_squared = 0
            for i in range(K + 1):
                expected = N * pi[i]
                if expected > 0:
                    chi_squared += ((v[i] - expected) ** 2) / expected

            # Calcul de la P-value
            p_value = scipy.special.gammaincc(K / 2.0, chi_squared / 2.0)

            # Détermination du résultat
            test_status = TestStatusDeterminer.determine_status(p_value)

            return response_handler.get_response(
                p_value=p_value,
                test_status=test_status,
                additional_info={
                    "chi_squared": chi_squared,
                    "template": template,
                    "template_length": m,
                    "block_size": M,
                    "num_blocks": N,
                    "frequencies": v,
                    "expected_frequencies": [N * pi[i] for i in range(K + 1)],
                    "lambda": lambda_val,
                    "eta": eta
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )