from testsuite.test_utils.response import TestResponse
import scipy.special
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class LinearComplexityTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], M=500, decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test de complexité linéaire NIST sur une séquence de bits.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            M (int): La longueur des bits dans un bloc (recommandé: M = 500)
            decision_rule (float): Seuil de décision pour le test (default: 0.01)

        Returns:
            dict: Résultats du test contenant la p-value et la décision (True si la séquence passe le test)
        """
        response_handler = TestResponse('Test de complexité linéaire')

        try:
            # Validation de la séquence
            n = len(bit_sequence)

            # Vérification que la séquence est assez longue pour au moins un bloc
            if n < M:
                return response_handler.get_response(
                    error=True,
                    error_message=f"La séquence est trop courte (minimum {M} bits requis)"
                )

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )

            # 1. Diviser la séquence en N blocs de M bits
            N = n // M
            blocks = [bit_sequence[i*M:(i+1)*M] for i in range(N)]

            # 2. Calculer la complexité linéaire Li pour chaque bloc
            L_values = [LinearComplexityTest.berlekamp_massey(block) for block in blocks]

            # 3. Calculer la moyenne théorique μ
            mu = M/2 + (9 + (-1)**(M+1))/36 - (M/3 + 2/9)/2**M

            # 4. Calculer Ti pour chaque bloc
            T = [((-1)**M * (Li - mu) + 2/9) for Li in L_values]

            # 5. Compter les occurrences dans les intervalles v0 à v6
            v = [0] * 7
            for Ti in T:
                if Ti <= -2.5:
                    v[0] += 1
                elif Ti <= -1.5:
                    v[1] += 1
                elif Ti <= -0.5:
                    v[2] += 1
                elif Ti <= 0.5:
                    v[3] += 1
                elif Ti <= 1.5:
                    v[4] += 1
                elif Ti <= 2.5:
                    v[5] += 1
                else:
                    v[6] += 1

            # 6. Calculer chi_square
            pi = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]
            chi_square = sum(((v[i] - N * pi[i])**2)/(N * pi[i]) for i in range(7))

            # 7. Calculer P-value
            p_value = scipy.special.gammainc(3, chi_square/2)

            # Détermination du résultat
            test_status = TestStatusDeterminer.determine_status(p_value)

            return response_handler.get_response(
                p_value=p_value,
                test_status=test_status,
                additional_info={
                    "block_size": M,
                    "number_of_blocks": N,
                    "theoretical_mean": mu,
                    "chi_square": chi_square,
                    "frequency_count": v
                }
            )
        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )

    @staticmethod
    def berlekamp_massey(block: list):
        """
        Implémentation de l'algorithme de Berlekamp-Massey pour calculer
        la complexité linéaire d'une séquence.

        Arguments:
            block (list): Séquence de bits à analyser

        Retourne:
            int: Complexité linéaire de la séquence
        """
        n = len(block)
        c = [0] * (n + 1)
        b = [0] * (n + 1)
        c[0] = b[0] = 1
        L = 0
        m = -1

        for N in range(n):
            d = block[N]
            for i in range(1, L + 1):
                d ^= c[i] & block[N - i]

            if d:
                t = c[:]
                for i in range(n - N + m):
                    if b[i]:
                        c[N - m + i] ^= 1
                if L <= N/2:
                    L = N + 1 - L
                    m = N
                    b = t

        return L
