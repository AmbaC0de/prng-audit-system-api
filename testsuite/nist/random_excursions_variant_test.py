import math
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class RandomExcursionsVariantTest:

    @staticmethod
    def run_test(bit_sequence: list[int]):
        """
        Effectue le test Random Excursions Variant NIST sur une séquence de bits.

        Args:
            bit_sequence(list[int] or str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            decision_rule(float): Seuil de décision pour le test (default: 0.01)

        Returns:
            dict: Résultats du test contenant les p-values pour chaque état et la décision
        """
        response_handler = TestResponse('Test des excursions aléatoires – variante')

        try:
            n = len(bit_sequence)

            # Validation de la séquence
            if n < 1000000:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 1,000,000 bits requis)"
                )

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )

            # Conversion des 0 en -1 et calcul de la marche aléatoire cumulative
            _seq = [2 * i - 1 for i in bit_sequence]

            # Calcul de la marche aléatoire cumulative S_k
            cumulative_sum = [0]
            for bit in _seq:
                cumulative_sum.append(cumulative_sum[-1] + bit)

            cumulative_sum.append(0)

            # Détermination du nombre de cycles J
            j = 0
            for i in range(1, len(cumulative_sum)):
                if cumulative_sum[i] == 0:
                    j += 1

            # Vérification que J >= 500 (condition NIST)
            if j < 500:
                return response_handler.get_response(
                    error=True,
                    error_message=f"Nombre de cycles insuffisant: J={j} < 500. Test non applicable."
                )

            # États à tester : x ∈ {-9, -8, ..., -1, +1, +2, ..., +8, +9}
            states = list(range(-9, 0)) + list(range(1, 10))

            p_values = {}
            test_results = {}

            for x in states:
                # Compter le nombre de fois où S_k = x
                count = sum(1 for s in cumulative_sum if s == x)

                # Calcul de la p-value pour cet état
                if j == 0:
                    p_value = 0.0
                else:
                    # P-value utilisant la fonction complémentaire d'erreur
                    p_value = math.erfc(abs((count - j) / math.sqrt(2 * j * ((4 * abs(x)) - 2))))

                p_values[f'state_{x}'] = p_value

                # Détermination du statut pour cet état
                test_results[f'state_{x}'] = TestStatusDeterminer.determine_status(p_value)

            min_p_value = min(p_values.values())

            test_status = TestStatusDeterminer.determine_status(min_p_value)

            return response_handler.get_response(
                p_value=p_values.values(),
                test_status=test_status,
                additional_info={
                    "p-values": p_values,
                    "test-results": test_results
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )