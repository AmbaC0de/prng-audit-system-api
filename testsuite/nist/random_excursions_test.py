from testsuite.test_utils.response import TestResponse
import numpy as np
import scipy.stats
from testsuite.test_utils.test_status_determiner import TestStatusDeterminer


class RandomExcursionsTest:
    DEFAULT_DECISION_RULE = 0.01
    STATES = [-4, -3, -2, -1, 1, 2, 3, 4]
    MIN_CYCLES = 500

    @staticmethod
    def run_test(bit_sequence: list[int], decision_rule=DEFAULT_DECISION_RULE):
        response_handler = TestResponse("Test d'excursion aléatoire")

        try:
            n = len(bit_sequence)
            # Convertir en marche aléatoire
            x = np.array([1 if b == 1 else -1 for b in bit_sequence])
            s = np.concatenate([[0], np.cumsum(x)])

            # Trouver les positions des zéros
            zero_positions = np.where(s == 0)[0]
            J = len(zero_positions)  # Nombre de cycles


            # Vérifier le nombre minimal de cycles
            if J < RandomExcursionsTest.MIN_CYCLES:
                return response_handler.get_response(
                    error=True,
                    error_message=f"Nombre insuffisant de cycles ({J}<{RandomExcursionsTest.MIN_CYCLES})"
                )

            # Compter les visites par état et par cycle
            state_cycle_counts = {state: np.zeros(J, dtype=int) for state in RandomExcursionsTest.STATES}

            for cycle_idx in range(J):
                start = zero_positions[cycle_idx]
                end = zero_positions[cycle_idx + 1] if cycle_idx < J - 1 else len(s)

                # Compter les occurrences de chaque état dans le cycle
                for state in RandomExcursionsTest.STATES:
                    state_cycle_counts[state][cycle_idx] = np.sum(s[start:end] == state)

            # Calcul des p-valeurs pour chaque état
            p_values = {}
            skipped_states = []
            for state in RandomExcursionsTest.STATES:
                abs_state = abs(state)
                counts = state_cycle_counts[state]

                # Calcul des probabilités théoriques
                pi = np.zeros(6)
                pi[0] = 1 - 1 / (2 * abs_state)  # Probabilité de 0 visite

                for k in range(1, 6):
                    if 1 <= k < 5:
                        pi[k] = (1/(4*abs_state**2))*(1-1/(2*abs_state))**(k-1)
                    if k == 5:
                        pi[k] = (1/(2*abs_state))*(1-1/(2*abs_state))**4

                # Vérifier les fréquences attendues
                expected = J * pi

                # Distribution des fréquences observées
                freq = np.zeros(6)
                for count in counts:
                    k = count if count < 5 else 5
                    freq[k] += 1
                # Statistique du khi-deux
                chi_sq = np.sum((freq - expected) ** 2 / expected)
                p_value = scipy.special.gammainc(5/2, chi_sq/2)
                p_values[state] = p_value

            # Déterminer le résultat global
            if not p_values:
                return response_handler.get_response(
                    error=True,
                    error_message="Tous les états ont été exclus (fréquences attendues < 5)"
                )

            min_p_value = min(p_values.values())
            test_status = TestStatusDeterminer.determine_status(min_p_value)

            return response_handler.get_response(
                p_value=min_p_value,
                test_status=test_status,
                additional_info={
                    "P-valeurs par état": {
                        f"État {state}": round(p_val, 5) for state, p_val in p_values.items()
                    }
                }
            )

        except Exception as e:
            return response_handler.get_response(
                error=True,
                error_message=f"Erreur d'exécution: {str(e)}"
            )