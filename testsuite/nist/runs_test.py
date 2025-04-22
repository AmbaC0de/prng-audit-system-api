from testsuite.test_utils.response import TestResponse
import math
import scipy


class RunsTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test de runs NIST sur une séquence de bits.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester
            decision_rule (float): Seuil de décision (par défaut: 0.01)

        Returns:
            dict: Résultats du test
        """
        response_handler = TestResponse('Test de runs')

        try:
            n = len(bit_sequence)

            # Validation de la séquence
            if n < 100:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 100 bits requis)"
                )

            # Étape 1: Calcul de la fréquence de 1 dans la séquence
            pi = sum(bit_sequence) / n

            # Étape 2: Calcul du nombre de runs r
            r = 1  # le premier "run" est compté
            for i in range(n - 1):
                if bit_sequence[i] != bit_sequence[i + 1]:
                    r += 1

            # Vérification de la condition NIST pour le test de runs
            if abs(pi - 0.5) >= 2 / math.sqrt(n):
                return response_handler.get_response(
                    error=True,
                    error_message="Le test de runs ne peut pas être effectué - "
                                  "la proportion de 1 (pi) est trop éloignée de 0.5"
                )

            # Étape 3: Calcul de la statistique du test
            vn_obs = r
            expected_runs = 2 * n * pi * (1 - pi)
            std_dev = math.sqrt(2 * n) * pi * (1 - pi)
            test_statistic = abs(vn_obs - expected_runs) / (2 * std_dev)

            # Étape 4: Calcul de la p-value
            p_value = 1 - scipy.special.erf(test_statistic)

            # Détermination du résultat
            is_random = p_value >= decision_rule

            return response_handler.get_response(
                p_value=p_value,
                is_random=is_random,
            )


        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )

