from testsuite.test_utils.response import TestResponse
import scipy.special



class NonOverlappingTemplateMatchingTest:
    DEFAULT_DECISION_RULE = 0.01

    @staticmethod
    def run_test(bit_sequence: list[int], template='000000001', decision_rule=DEFAULT_DECISION_RULE):
        """
        Effectue le test de non-chevauchement de modèles NIST sur une séquence de bits.

        Args:
            bit_sequence (list[int] ou str): La séquence de bits à tester (liste ou chaîne de '0' et '1')
            m (int): Longueur du modèle à rechercher (default: 9)
            template (str): Le modèle à rechercher dans la séquence (default: '000000001')
            decision_rule (float): Seuil de décision pour le test (default: 0.01)

        Returns:
            dict: Résultats du test contenant la p-value et la décision (True si la séquence passe le test)
        """
        response_handler = TestResponse('Test de non-chevauchement de modèles')

        try:
            n = len(bit_sequence)
            m = len(template)

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

            # Vérification que m est dans la plage recommandée
            if m < 2 or m > 10:
                return response_handler.get_response(
                    error=True,
                    error_message=f"La longueur du modèle m={m} est en dehors de la plage recommandée (2-10). Pour des résultats significatifs, m=9 ou m=10 est fortement recommandé."
                )

            # Conversion du modèle en liste d'entiers
            if isinstance(template, str):
                template = [int(bit) for bit in template]

            # Calcul des paramètres selon les recommandations du NIST
            # M > 0.01*n et N = ⌊n/M⌋, avec N ≤ 100
            M = max(int(0.01 * n + 1), m + 1)  # M doit être supérieur à 0.01*n et assez grand pour contenir le modèle
            N = min(n // M, 100)  # N ne doit pas dépasser 100 pour assurer la validité des p-values

            # Si la séquence est trop courte pour au moins un bloc
            if N < 1:
                return response_handler.get_response(
                    error=True,
                    error_message=f"La séquence est trop courte pour la taille de bloc M={M}"
                )

            # Tronquer la séquence au multiple de M
            bit_sequence = bit_sequence[:N * M]

            # Compter les occurrences du modèle dans chaque bloc
            W = []
            for i in range(N):
                block = bit_sequence[i * M:(i + 1) * M]
                count = 0
                j = 0
                while j <= M - m:
                    if block[j:j + m] == template:
                        count += 1
                        j += m  # Avancer à la position après le modèle (non-chevauchement)
                    else:
                        j += 1
                W.append(count)

            # Calcul des statistiques
            mu = (M - m + 1) / (2 ** m)
            sigma2 = M * ((1 / (2 ** m)) - ((2 * m - 1) / (2 ** (2 * m))))

            # Calcul du chi carré
            chi_square = sum([(w - mu) ** 2 / sigma2 for w in W])

            # Calcul de la p-value
            p_value = scipy.special.gammaincc(N / 2, chi_square / 2)

            # Détermination du résultat
            is_random = p_value >= decision_rule

            return response_handler.get_response(
                p_value=p_value,
                is_random=is_random,
                additional_info={
                    "number_of_blocks": N,
                    "block_size": M,
                    "template": ''.join(str(bit) for bit in template),
                    "template_occurrences": W
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )
