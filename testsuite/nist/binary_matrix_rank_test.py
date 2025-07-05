from testsuite.test_utils.response import TestResponse
import numpy as np
import math
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class BinaryMatrixRankTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test de rang de matrices binaires NIST sur une séquence de bits.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            decision_rule (float): Seuil de décision pour le test (default: 0.01)

        Returns:
            dict: Résultats du test contenant la p-value et la décision (True si la séquence passe le test)
        """
        response_handler = TestResponse('Test de rang de matrices binaires')

        try:
            # Paramètres de test
            M = 32  # Nombre de lignes de chaque sous-matrice
            Q = 32  # Nombre de colonnes de chaque sous-matrice

            # Validation de la séquence
            n = len(bit_sequence)
            if n < 38 * M * Q:  # Selon la NIST SP 800-22
                return response_handler.get_response(
                    error=True,
                    error_message=f"La séquence est trop courte (minimum {38*M*Q} bits requis)"
                )

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )

            # Nombre de matrices complètes possibles
            N = n // (M * Q)

            # Création des matrices
            matrices = []
            for i in range(N):
                start = i * M * Q
                block = bit_sequence[start:start + M * Q]
                # Reshape le bloc en matrice M x Q
                matrix = np.array(block).reshape(M, Q)
                matrices.append(matrix)

            # Calculer le rang de chaque matrice
            ranks = [np.linalg.matrix_rank(matrix) for matrix in matrices]

            # Compter les matrices selon leur rang
            FM = sum(1 for r in ranks if r == M)        # Nombre de matrices de rang complet
            FM1 = sum(1 for r in ranks if r == M - 1)   # Nombre de matrices de rang M-1
            remaining = N - FM - FM1                    # Matrices de rang inférieur

            # Calculer chi carré
            # Les valeurs 0.2888, 0.5776 et 0.1336 sont les probabilités théoriques
            # pour les différentes catégories de rang selon NIST SP 800-22
            chi_square = (
                    ((FM - 0.2888 * N)**2) / (0.2888 * N) +
                    ((FM1 - 0.5776 * N)**2) / (0.5776 * N) +
                    ((remaining - 0.1336 * N)**2) / (0.1336 * N)
            )

            # Calculer la P-value
            p_value = math.exp(-chi_square / 2)

            # Détermination du résultat
            test_status = TestStatusDeterminer.determine_status(p_value)

            return response_handler.get_response(
                p_value=p_value,
                test_status=test_status,
                additional_info={
                    "Nombre total de matrices analysées": N,
                    "Rangs observés": f"{FM} matrices de rang complet, {FM1} de rang {M - 1}, {remaining} de rang inférieur",
                    "Dimensions des matrices": f"{M}x{Q}",
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )
