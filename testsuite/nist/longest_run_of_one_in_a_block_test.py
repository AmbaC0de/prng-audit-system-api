from testsuite.test_utils.response import TestResponse
import math
import numpy as np
import scipy.special
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class LongestRunOfOneInABlockTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test du plus long run de uns dans un bloc selon la méthode NIST SP 800-22.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester
            decision_rule (float): Seuil de décision (par défaut: 0.01)

        Returns:
            dict: Résultats du test
        """
        response_handler = TestResponse('Test du plus long run de 1 dans un bloc')

        try:

            n = len(bit_sequence)

            # Détermination de M et des paramètres en fonction de la longueur de la séquence
            if n < 128:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 128 bits requis)"
                )
            elif 128 <= n < 6272:
                M = 8
                K = 3
                N = 16
                v_values = [1, 2, 3, 4]  # v0, v1, v2, v3 où v0 ≤ 1, v3  ≥4
                pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
            elif 6272 <= n < 750000:
                M = 128
                K = 5
                N = 49
                v_values = [4, 5, 6, 7, 8, 9]  # v0, v1, v2, v3, v4, v5 où v0 est ≤4, v5 est ≥9
                pi_values = [ 0.1174,  0.2430, 0.2493, 0.1752,  0.1027,  0.1124]  # Ref Section 3.4 du document NIST
            else:
                M = 10000
                K = 6
                N = 75
                v_values = [10, 11, 12, 13, 14, 15, 16]  # v0, v1, v2, v3, v4, v5, v6 où v0 est ≤10, v6 est ≥16
                pi_values = [ 0.0882,  0.2092,  0.2483,  0.1933,  0.1208, 0.0675,  0.0727]  # Ref Section 3.4 du document NIST

            # Si les pi_values ne sont pas disponibles, nous ne pouvons pas effectuer le test
            if pi_values is None:
                return response_handler.get_response(
                    error=True,
                    error_message="Les valeurs de probabilité ne sont pas disponibles pour cette longueur de séquence"
                )

            # Division de la séquence en blocs de taille M
            num_blocks = n // M
            if num_blocks < N:
                return response_handler.get_response(
                    error=True,
                    error_message=f"Nombre de blocs insuffisant. Requis: {N}, Obtenu: {num_blocks}"
                )

            # Compter le plus long run de uns dans chaque bloc
            v = [0] * (K + 1)  # Tableau pour stocker les fréquences

            for i in range(N):
                block = bit_sequence[i * M:(i + 1) * M]
                max_run = 0
                current_run = 0

                for bit in block:
                    if bit == 1:
                        current_run += 1
                        max_run = max(max_run, current_run)
                    else:
                        current_run = 0

                # Catégoriser le plus long run selon les intervalles v_values
                if max_run <= v_values[0]:
                    v[0] += 1
                elif max_run >= v_values[-1]:
                    v[-1] += 1
                else:
                    for j in range(1, len(v_values)):
                        if max_run == v_values[j-1] + (j-1):
                            v[j] += 1
                            break

            # Calcul de la statistique de test chi-carré
            chi_squared = 0
            for i in range(K + 1):
                expected = N * pi_values[i]
                chi_squared += ((v[i] - expected) ** 2) / expected

            # Calcul de la P-value
            p_value = scipy.special.gammaincc(K / 2, chi_squared / 2)

            # Détermination du résultat
            test_status = TestStatusDeterminer.determine_status(p_value)

            return response_handler.get_response(
                p_value=p_value,
                test_status=test_status,
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )
