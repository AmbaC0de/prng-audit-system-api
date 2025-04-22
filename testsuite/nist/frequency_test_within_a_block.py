from testsuite.test_utils.response import TestResponse
import scipy



class FrequencyTestWithinABlock:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        response_handler = TestResponse('Test de fréquence par block')

        try:
            n = len(bit_sequence)

            if n < 100:
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 100 bits requis)"
                )
            # Obtenir une taille de bloc normalisee
            block_size = FrequencyTestWithinABlock.determine_block_size(n)
            if block_size is None:
                return response_handler.get_response(
                    error=True,
                    error_message="Impossible de déterminer une taille de bloc convenable"
                )

            observation = 0
            number_of_blocks = int(n/block_size)
            for j in range(1, number_of_blocks + 1):
                pi_j = 0
                for i in range(block_size):
                    pi_j = pi_j + bit_sequence[(j-1) * block_size + i] / block_size
                observation = observation + (pi_j - 0.5)**2

            x_2_observation = 4 * block_size * observation
            p_value = 1 - scipy.special.gammainc(number_of_blocks/2, x_2_observation/2)
            is_random = p_value >= decision_rule

            return response_handler.get_response(
                p_value=p_value,
                is_random=is_random
            )
        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )


    @staticmethod
    def determine_block_size(sequence_length: int):
        """
        Détermine une taille de bloc appropriée selon les recommandations NIST.

        Args:
            sequence_length (int): Longueur de la séquence à tester

        Returns:
            int or None: Taille de bloc recommandée ou None si impossible
        """
        if sequence_length < 100:
            return None

        # Essayer différentes tailles de bloc jusqu'à trouver une convenable
        for m in range(20, int(sequence_length/2) + 1):
            n = sequence_length
            N = int(n/m)  # nombre de blocs

            # Vérifier les conditions: M ≥ 20, M > .01n et N < 100
            if m >= 20 and m > 0.01 * n and N < 100:
                return m

        return None  # Aucune taille de bloc convenable trouvée
