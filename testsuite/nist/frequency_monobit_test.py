import math
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class FrequencyMonobitTest:
    @staticmethod
    def run_test(bit_sequence: list[int]):
        """
        Effectue le test de fréquence monobit NIST sur une séquence de bits.

        Args:
            bit_sequence(list[int] or str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
        Returns:
            dict: Résultats du test contenant la p-value et la décision (True si la séquence passe le test)
        """
        response_handler = TestResponse('Test de fréquence monobit')

        try:
            n = len(bit_sequence)

            # Validation de la séquence
            if n < 100:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 100 bits requis)"
                )

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )
            # Conversion des 0 en -1
            _seq = [2*i - 1 for i in bit_sequence]
            s_n = abs(sum(_seq))
            s_obs = s_n / math.sqrt(n)
            p_value = math.erfc(s_obs / math.sqrt(2))

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
