import math
from scipy.stats import norm
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class CumulativeSumsTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def _compute_p(x_seq: list[int]):
        """Calcul de la p-value"""
        n = len(x_seq)
        S = [0] * (n + 1)
        for i in range(1, n + 1):
            S[i] = S[i - 1] + x_seq[i - 1]
        z = max(abs(s) for s in S)
        z_norm = z / math.sqrt(n)
        # p-value formula de NIST
        sum1 = 0.0
        k_min = int(math.ceil((-n / z) + 1) / 4)
        k_max = int(math.floor((n / z - 1) / 4))
        for k in range(k_min, k_max + 1):
            sum1 += norm.cdf((4 * k + 1) * z_norm) - norm.cdf((4 * k - 1) * z_norm)
        sum2 = 0.0
        k_min2 = int(math.ceil((-n / z - 1) / 4))
        k_max2 = int(math.floor((n / z - 3) / 4))
        for k in range(k_min2, k_max2 + 1):
            sum2 += norm.cdf((4 * k + 3) * z_norm) - norm.cdf((4 * k + 1) * z_norm)
        p_val = 1.0 - sum1 + sum2
        return p_val

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le Cumulative Sums (Cusum) Test NIST SP 800-22.
        Args:
            bit_sequence (list[int]): Séquence de bits (0/1)
            decision_rule (float): seuil p-value (défaut 0.01)
        Returns:
            dict: p-values (forward/backward) et statut de test
        """
        response = TestResponse("Test de somme cumulative")
        try:
            n = len(bit_sequence)

            if not all(b in (0, 1) for b in bit_sequence):
                return response.get_response(error=True, error_message="Bits invalides (attendu 0 ou 1)")

            X = [2*b - 1 for b in bit_sequence]

            # test avant (forward) et arrière (backward)
            p_forward = CumulativeSumsTest._compute_p(X)
            p_backward = CumulativeSumsTest._compute_p(list(reversed(X)))

            status = TestStatusDeterminer.determine_status([p_forward, p_backward])

            return response.get_response(
                p_value=[p_forward, p_backward],
                test_status=status,
            )

        except Exception as e:
            return response.get_response(error=True, error_message=f"Erreur lors du test: {e}")
