import math
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class ApproximateEntropyTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def _max_of_runs(bit_sequence, pattern_length):
        """
        Calcule les occurrences de tous les patterns de longueur donnée
        """
        n = len(bit_sequence)
        patterns = {}

        # Créer une séquence circulaire en ajoutant les premiers (pattern_length-1) bits à la fin
        extended_sequence = bit_sequence + bit_sequence[:pattern_length - 1]

        # Compter les occurrences de chaque pattern
        for i in range(n):
            pattern = tuple(extended_sequence[i:i + pattern_length])
            patterns[pattern] = patterns.get(pattern, 0) + 1

        return patterns

    @staticmethod
    def _calculate_phi(bit_sequence, pattern_length):
        """
        Calcule la fonction phi(m) pour une longueur de pattern donnée
        """
        n = len(bit_sequence)
        patterns = ApproximateEntropyTest._max_of_runs(bit_sequence, pattern_length)

        phi = 0.0
        for count in patterns.values():
            if count > 0:
                probability = count / n
                phi += probability * math.log(probability)

        return phi

    @staticmethod
    def run_test(bit_sequence: list[int], m=2):
        """
        Effectue le test d'entropie approximative NIST sur une séquence de bits.

        Args:
            bit_sequence(list[int] or str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            m(int): Longueur du pattern m (default: calculé automatiquement selon NIST)

        Returns:
            dict: Résultats du test contenant la p-value et la décision
        """
        response_handler = TestResponse("Test d'entropie approximative")

        try:
            n = len(bit_sequence)

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )


            # Validation de m
            if m <= 0 or m >= math.log2(n):
                return response_handler.get_response(
                    error=True,
                    error_message=f"Longueur de motif invalide m={m}. Doit être: 0 < m < log2(n)"
                )

            # Calcul de phi(m) et phi(m+1)
            phi_m = ApproximateEntropyTest._calculate_phi(bit_sequence, m)
            phi_m_plus_1 = ApproximateEntropyTest._calculate_phi(bit_sequence, m + 1)

            # Calcul de l'entropie approximative
            apen = phi_m - phi_m_plus_1

            # Calcul de la statistique de test selon NIST
            chi_squared = 2 * n * (math.log(2) - apen)

            # Calcul de la p-value using chi-squared distribution with 2^m degrees of freedom
            degrees_of_freedom = 2 ** m

            # Approximation de la p-value pour une distribution chi-carré
            # Utilisation de la fonction gamma incomplète
            try:
                from scipy.special import gammaincc
                p_value = gammaincc(degrees_of_freedom / 2, chi_squared / 2)
            except ImportError:
                # Approximation alternative si scipy n'est pas disponible
                # Utilisation de l'approximation normale pour grands degrés de liberté
                if degrees_of_freedom > 30:
                    z = (chi_squared - degrees_of_freedom) / math.sqrt(2 * degrees_of_freedom)
                    p_value = 0.5 * math.erfc(z / math.sqrt(2))
                else:
                    # Pour de petits degrés de liberté, approximation simple
                    p_value = math.exp(-chi_squared / 2)

            # Assurer que p_value est dans [0, 1]
            p_value = max(0.0, min(1.0, p_value))

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