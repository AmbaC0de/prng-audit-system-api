from testsuite.test_utils.response import TestResponse


class BerlekampMassey:
    @staticmethod
    def format_polynomial(coeffs: list[int]) -> str:
        """
        Formate un polynôme représenté par ses coefficients pour un affichage lisible.

        Args:
            coeffs: Liste des coefficients [a0, a1, a2, ...] représentant a0 + a1*x + a2*x² + ...

        Returns:
            String représentant le polynôme formaté
        """
        if not coeffs or all(c == 0 for c in coeffs):
            return "0"

        terms = []

        for i, coeff in enumerate(coeffs):
            if coeff == 0:
                continue

            if i == 0:
                # Terme constant
                terms.append("1")
            elif i == 1:
                # Terme en x
                terms.append("x")
            else:
                # Termes en x^n
                terms.append(f"x^{i}")

        if not terms:
            return "0"

        # Joindre les termes avec des "+"
        result = " + ".join(terms)

        # Si le polynôme commence par x (pas de terme constant),
        # on peut le laisser tel quel
        return result

    @staticmethod
    def run_test(sequence: list[int]):
        """
        Implémentation de l'algorithme de Berlekamp-Massey pour calculer
        la complexité linéaire d'une séquence.
        """

        response_handler = TestResponse("Berlkamp-Massey")

        try:
            n = len(sequence)
            p_x = [1] + [0] * n  # Polynôme de connexion
            q_x = [1] + [0] * n  # Polynôme auxiliaire
            L = 0  # Longueur du LFSR
            m = -1  # Distance depuis la dernière mise à jour
            d = 0  # Discordance actuelle
            t_x = [1] + [0] * n  # Polynôme temporaire

            for k in range(n):
                # calcul du syndrome d'erreur
                d = sequence[k]
                for i in range(1, L + 1):
                    d ^= p_x[i] * sequence[k - i]
                # En cas d'erreur on corrige le polynôme de connexion
                if d != 0:
                    # Copier p_x dans t_x
                    t_x = p_x[:]
                    # S'assurer que p_x est suffisamment long
                    if len(p_x) < len(q_x) + k - m:
                        p_x.extend([0] * (len(q_x) + k - m - len(p_x)))

                    # Mettre à jour p_x en ajoutant q_x décalé.
                    # Pour chaque terme q_j de Q(x), nous mettons à jour le terme correspondant p_k-m+j de P(x)
                    # par une opération XOR (addition dans le corps fini GF(2)).
                    for j in range(len(q_x)):
                        p_x[k - m + j] ^= q_x[j]

                    if 2 * L <= k:
                        L = k + 1 - L
                        m = k
                        q_x = t_x

            # Nettoyer le polynôme en supprimant les zéros à la fin
            while len(p_x) > 1 and p_x[-1] == 0:
                p_x.pop()

            return response_handler.get_response(
                test_status='attack_success',
                additional_info={
                    "Complexité": L,
                    "Polynome": BerlekampMassey.format_polynomial(p_x),
                    "Coefficients": p_x  # Garder aussi les coefficients bruts si nécessaire
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )