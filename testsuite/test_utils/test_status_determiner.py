from testsuite.test_utils.nist_parameters import NistTestParameters
class TestStatusDeterminer:
    """
    Classe utilitaire pour déterminer le statut des tests basé sur la p-value.
    """

    STATUS_MESSAGES = {
            "success": "La séquence est aléatoire pour ce test",
            "failed": "La séquence n'est pas aléatoire pour ce test",
            "warning": "La séquence présente des résultats ambigus (proche du seuil de décision)"
        }

    @staticmethod
    def determine_status(p_value,
                         decision_rule: float = NistTestParameters.DEFAULT_DECISION_RULE,
                         warning_threshold: float = NistTestParameters.DEFAULT_WARNING_THRESHOLD) -> str:
        """
        Détermine le statut basé sur la/les p-value(s) et les seuils.

        Args:
            p_value (float or list/tuple): La p-value calculée ou une liste/tuple de p-values
            decision_rule (float): Seuil de décision principal
            warning_threshold (float): Demi-largeur de l'intervalle de warning

        Returns:
            str: 'success', 'failed', ou 'warning'
        """
        # Gérer le cas d'une seule p-value (rétrocompatibilité)
        if isinstance(p_value, (int, float)):
            return TestStatusDeterminer._evaluate_single_p_value(p_value, decision_rule, warning_threshold)

        # Gérer le cas de plusieurs p-values
        elif isinstance(p_value, (list, tuple)):
            if len(p_value) == 0:
                raise ValueError("La liste de p-values ne peut pas être vide")

            # Évaluer chaque p-value individuellement
            statuses = [TestStatusDeterminer._evaluate_single_p_value(pv, decision_rule, warning_threshold)
                        for pv in p_value]

            # Déterminer le statut global selon la logique suivante :
            # - Si au moins une p-value est 'failed' → 'failed'
            # - Si toutes sont 'success' → 'success'
            # - Sinon (mélange de success/warning ou présence de warning) → 'warning'
            if 'failed' in statuses:
                return 'failed'
            elif all(status == 'success' for status in statuses):
                return 'success'
            else:
                return 'warning'

        else:
            raise TypeError("p_value doit être un nombre ou une liste/tuple de nombres")

    @staticmethod
    def _evaluate_single_p_value(p_value: float,
                                 decision_rule: float,
                                 warning_threshold: float) -> str:
        """
        Évalue une seule p-value et retourne son statut.

        Args:
            p_value (float): La p-value à évaluer
            decision_rule (float): Seuil de décision principal
            warning_threshold (float): Demi-largeur de l'intervalle de warning

        Returns:
            str: 'success', 'failed', ou 'warning'
        """
        # Définir les bornes de la zone de warning
        warning_lower = decision_rule - warning_threshold
        warning_upper = decision_rule + warning_threshold

        if p_value >= warning_upper:
            return 'success'  # Clairement aléatoire
        elif p_value <= warning_lower:
            return 'failed'  # Clairement non-aléatoire
        else:
            return 'warning'  # Zone d'incertitude

    @staticmethod
    def get_status_message(status: str) -> str:
        """
        Retourne le message correspondant au statut.

        Args:
            status (str): Le statut ('success', 'failed', 'warning')

        Returns:
            str: Message descriptif du statut
        """
        return TestStatusDeterminer.STATUS_MESSAGES.get(status, "Statut de test inconnu")