import math
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class MaurerUniversalTest:
    DEFAULT_DECISION_RULE = 0.01
    # Configuration des paramètres pour le test de Maurer selon NIST
    # La cle du dictionnaire represente la taille de la sequence
    MAURER_CONFIG = {
        1059061760: {'L': 16, 'Q': 655360, 'expected': 15.167379, 'variance': 3.421},
        496435200: {'L': 15, 'Q': 327680, 'expected': 14.167488, 'variance': 3.419},
        231669760: {'L': 14, 'Q': 163840, 'expected': 13.167693, 'variance': 3.416},
        107560960: {'L': 13, 'Q': 81920, 'expected': 12.168070, 'variance': 3.410},
        49643520: {'L': 12, 'Q': 40960, 'expected': 11.168765, 'variance': 3.401},
        22753280: {'L': 11, 'Q': 20480, 'expected': 10.170032, 'variance': 3.384},
        10342400: {'L': 10, 'Q': 10240, 'expected': 9.1723243, 'variance': 3.356},
        4654080: {'L': 9, 'Q': 5120, 'expected': 8.1764248, 'variance': 3.311},
        2068480: {'L': 8, 'Q': 2560, 'expected': 7.1836656, 'variance': 3.238},
        904960: {'L': 7, 'Q': 1280, 'expected': 6.1962507, 'variance': 3.125},
        387840: {'L': 6, 'Q': 640, 'expected': 5.2177052, 'variance': 2.954}
    }

    # Fonction pour déterminer les paramètres
    @staticmethod
    def get_maurer_parameters(n):
        """Détermine les paramètres L, Q, expected et variance selon la longueur n"""
        for min_length in sorted(MaurerUniversalTest.MAURER_CONFIG.keys(), reverse=True):
            if n >= min_length:
                return MaurerUniversalTest.MAURER_CONFIG[min_length]
        return None

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test statistique universel de Maurer NIST sur une séquence de bits.

        Args:
            bit_sequence(list[int] or str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            decision_rule(float): Seuil de décision pour le test (default: 0.01)

        Returns:
            dict: Résultats du test contenant la p-value et la décision
        """
        response_handler = TestResponse('Test statistique universel de Maurer')

        try:
            n = len(bit_sequence)

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )

            params = MaurerUniversalTest.get_maurer_parameters(n)

            if n < 387840:  # Minimum requis selon NIST
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte (minimum 387840 bits requis)"
                )

            L = params['L']
            Q = params['Q']
            K = n // L - Q  # Nombre de blocs dans le segment de test

            expected_value = params['expected']
            variance = params['variance']

            if K <= 0:
                return response_handler.get_response(
                    error=True,
                    error_message="Paramètres invalides: K doit être positif"
                )

            # Étape 1: Initialisation de la table
            T = {}

            # Étape 2: Initialisation (segment d'initialisation)
            for i in range(Q):
                block = 0
                for j in range(L):
                    block = (block << 1) + bit_sequence[i * L + j]
                T[block] = i + 1

            # Étape 3: Calcul de la statistique (segment de test)
            sum_log = 0.0

            for i in range(Q, Q + K):
                block = 0
                for j in range(L):
                    block = (block << 1) + bit_sequence[i * L + j]

                if block in T:
                    distance = i + 1 - T[block]
                    sum_log += math.log2(distance)
                else:
                    # Si le bloc n'a jamais été vu, distance = i + 1
                    sum_log += math.log2(i + 1)

                T[block] = i + 1

            # Calcul de la statistique de test
            fn = sum_log / K

            c = 0.7 - 0.8 / L + (4 + 32 / L) * pow(K, -3 / L) / 15
            sigma = c * math.sqrt(variance / K)

            # Calcul de la p-value
            arg = abs((fn - expected_value) / (math.sqrt(2) * sigma))
            p_value = math.erfc(arg)

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