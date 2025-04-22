class TestResponse:
    def __init__(self, test_name=""):
        self.test_name = test_name

    def get_response(self, p_value=None, is_random=None, error=None, error_message=None):
        """
        Génère une réponse standardisée pour les tests statistiques

        Args:
            p_value (float, optional): La p-value calculée
            is_random (bool, optional): Si la séquence est considérée comme aléatoire
            error (bool, optional): Si une erreur s'est produite
            error_message (str, optional): Message d'erreur spécifique

        Returns:
            dict: Réponse formatée pour l'API
        """
        if error:
            return {
                "error": True,
                "message": error_message or "Une erreur s'est produite lors du test",
                "p_value": None,
                "is_random": False,
                "test_name": self.test_name
            }

        return {
            "error": False,
            "p_value": p_value,
            "is_random": is_random,
            "message": "La séquence est aléatoire" if is_random else "La séquence n'est pas aléatoire",
            "test_name": self.test_name
        }
