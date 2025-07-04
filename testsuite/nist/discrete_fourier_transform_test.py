from testsuite.test_utils.response import TestResponse
import math
import numpy as np
import scipy.special
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer



class DiscreteFourierTransformTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test de transformation de Fourier discrète (spectral) selon la méthode NIST SP 800-22.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester
            decision_rule (float): Seuil de décision (par défaut: 0.01)

        Returns:
            dict: Résultats du test
        """
        response_handler = TestResponse('Test de transformation de Fourier discrète (spectral)')

        try:
            n = len(bit_sequence)

            # Vérification de la longueur minimale
            if n < 100:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 100 bits requis)"
                )

            # Étape 1: Conversion des 0 et 1 en valeurs -1 et +1
            X = [2*bit - 1 for bit in bit_sequence]


            # Étape 2: Application de la transformée de Fourier discrète (DFT)
            S = np.fft.fft(X)

            # Étape 3: Calcul de M = modulus(S') où S' est la sous-chaîne des premiers n/2 éléments
            # On prend seulement la première moitié du spectre (n/2 éléments)
            S_prime = S[1:n//2-1]
            M = np.abs(S_prime)

            # Étape 4: Calcul du seuil T (95% peak height threshold)
            T = math.sqrt(math.log(1/0.05) * n)

            # Étape 5: Calcul de N0 (nombre théorique attendu de pics < T sous hypothèse de randomness)
            N0 = 0.95 * n / 2

            # Étape 6: Calcul de N1 (nombre réel observé de pics < T)
            N1 = sum(1 for magnitude in M if magnitude < T)

            # Étape 7: Calcul de d (statistique de test normalisée)
            d = (N1 - N0) / math.sqrt((n * 0.95 * 0.05) / 4)

            # Étape 8: Calcul de la P-value
            p_value = scipy.special.erfc(abs(d) / math.sqrt(2))

            # Détermination du résultat
            test_status = TestStatusDeterminer.determine_status(p_value)

            return response_handler.get_response(
                p_value=p_value,
                test_status=test_status,
                additional_info={
                    "Méthode": "Analyse spectrale basée sur la transformée de Fourier discrète",
                    "Pics attendus (seuil 95%)": round(N0),
                    "Pics observés sous le seuil": N1,
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )