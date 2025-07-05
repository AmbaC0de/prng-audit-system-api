import scipy.special
from testsuite.test_utils.response import TestResponse
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class SerialTest:

    @staticmethod
    def run_test(bit_sequence: list[int], m=3):
        """
        Effectue le test sériel NIST sur une séquence de bits pour vérifier l'uniformité
        de distribution des motifs de m bits.

        Args:
            bit_sequence (list[int]): La séquence de bits à tester
            m (int): Longueur des motifs à analyser (default: 3)

        Returns:
            dict: Résultats du test contenant les p-values et la décision
        """
        response_handler = TestResponse('Test sériel')

        try:
            # Validation de la séquence
            n = len(bit_sequence)

            # Vérification que la longueur est suffisante
            if n < 100:  # Minimum arbitraire, mais raisonnable
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence est trop courte pour le test sériel"
                )

            # Vérification que m respecte la recommandation du NIST (m < ⌊log₂n⌋-2)
            import math
            max_m = math.floor(math.log2(n)) - 2
            if m >= max_m:
                return response_handler.get_response(
                    error=True,
                    error_message=f"Le paramètre m={m} est trop grand pour cette séquence. "
                                  f"Selon les recommandations NIST, m doit être < {max_m}"
                )

            # Vérification que la séquence ne contient que des 0 et des 1
            if not all(bit in [0, 1] for bit in bit_sequence):
                return response_handler.get_response(
                    error=True,
                    error_message="La séquence doit contenir uniquement des 0 et des 1"
                )

            # 1. Former une séquence augmentée en ajoutant les premiers m-1 bits à la fin
            augmented_sequence = bit_sequence.copy()
            for i in range(m - 1):
                augmented_sequence.append(bit_sequence[i])

            # 2. Compter les fréquences des motifs de m, m-1 et m-2 bits
            # Dictionnaires pour stocker les fréquences
            freq_m = {}      # Pour les motifs de m bits
            freq_m1 = {}     # Pour les motifs de m-1 bits
            freq_m2 = {}     # Pour les motifs de m-2 bits

            # Générer tous les motifs possibles de m bits
            for i in range(2**m):
                pattern = SerialTest._int_to_binary(i, m)
                freq_m[pattern] = 0

            # Générer tous les motifs possibles de m-1 bits
            for i in range(2**(m-1)):
                pattern = SerialTest._int_to_binary(i, m-1)
                freq_m1[pattern] = 0

            # Générer tous les motifs possibles de m-2 bits (si m >= 2)
            if m >= 2:
                for i in range(2**(m-2)):
                    pattern = SerialTest._int_to_binary(i, m-2)
                    freq_m2[pattern] = 0

            # Compter les fréquences des motifs dans la séquence augmentée
            for i in range(n):
                # Motif de m bits
                pattern_m = ''.join(str(augmented_sequence[i+j]) for j in range(m))
                freq_m[pattern_m] = freq_m.get(pattern_m, 0) + 1

                # Motif de m-1 bits
                pattern_m1 = ''.join(str(augmented_sequence[i+j]) for j in range(m-1))
                freq_m1[pattern_m1] = freq_m1.get(pattern_m1, 0) + 1

                # Motif de m-2 bits (si m >= 2)
                if m >= 2:
                    pattern_m2 = ''.join(str(augmented_sequence[i+j]) for j in range(m-2))
                    freq_m2[pattern_m2] = freq_m2.get(pattern_m2, 0) + 1

            # 3. Calculer les statistiques psi²
            psi_sq_m = 0
            for pattern, freq in freq_m.items():
                psi_sq_m += (freq - n/2**m)**2
            psi_sq_m = (2**m / n) * psi_sq_m

            psi_sq_m1 = 0
            for pattern, freq in freq_m1.items():
                psi_sq_m1 += (freq - n/2**(m-1))**2
            psi_sq_m1 = (2**(m-1) / n) * psi_sq_m1

            psi_sq_m2 = 0
            if m >= 2:
                for pattern, freq in freq_m2.items():
                    psi_sq_m2 += (freq - n/2**(m-2))**2
                psi_sq_m2 = (2**(m-2) / n) * psi_sq_m2

            # 4. Calculer del_psi²_m et del²_psi²_m
            del_psi_sq_m = psi_sq_m - psi_sq_m1
            del2_psi_sq_m = psi_sq_m - 2*psi_sq_m1 + psi_sq_m2 if m >= 2 else 0

            # 5. Calculer les p-values
            p_value1 = scipy.special.gammaincc(2**(m-2), del_psi_sq_m/2)
            p_value2 = scipy.special.gammaincc(2**(m-3), del2_psi_sq_m/2) if m >= 2 else 1.0

            # Décision finale (la séquence est considérée aléatoire si les deux p-values sont >= decision_rule)
            test_status = TestStatusDeterminer.determine_status([p_value1, p_value2])

            return response_handler.get_response(
                p_value=[p_value1, p_value2],
                test_status=test_status,
                additional_info={
                    "p-value 1 (Δψ²)": round(p_value1, 5),
                    "p-value 2 (Δ²ψ²)": round(p_value2, 5) if m >= 2 else "N/A"
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur lors de l'exécution du test: {str(e)}"
            )

    @staticmethod
    def _int_to_binary(n, width):
        """
        Convertit un entier en une chaîne binaire de largeur fixe.

        Args:
            n (int): L'entier à convertir
            width (int): La largeur de la chaîne binaire souhaitée

        Returns:
            str: Chaîne binaire de la largeur spécifiée
        """
        return format(n, f'0{width}b')
