class NistTestParameters:
    """
    Classe pour centraliser tous les paramètres par défaut des tests NIST.
    """
    # Paramètres de décision
    DEFAULT_DECISION_RULE = 0.01
    DEFAULT_WARNING_THRESHOLD = 0.002

    @classmethod
    def get_decision_rule(cls, custom_rule=None):
        """Retourne la règle de décision (custom ou par défaut)"""
        return custom_rule if custom_rule is not None else cls.DEFAULT_DECISION_RULE

    @classmethod
    def get_warning_threshold(cls, custom_threshold=None):
        """Retourne le seuil de warning (custom ou par défaut)"""
        return custom_threshold if custom_threshold is not None else cls.DEFAULT_WARNING_THRESHOLD
