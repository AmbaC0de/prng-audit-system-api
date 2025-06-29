from testsuite.test_utils.test_status_determiner import TestStatusDeterminer

class TestResponse:
    def __init__(self, test_name=""):
        self.test_name = test_name

    def get_response(self, p_value=None, test_status=None, error=None, error_message=None, additional_info=None):
        """
        Génère une réponse standardisée pour les tests statistiques

        Args:
            p_value (float, optional) : La p-value calculée
            is_random (bool, optional) : Si la séquence est considérée comme aléatoire
            error (bool, optional) : Si une erreur s'est produite
            error_message (str, optional) : Message d'erreur spécifique
            additional_info (dict, optional) : Informations supplémentaires sur le test

        Returns:
            dict: Réponse formatée pour l'API
        """
        if error:
            return {
                "error": True,
                "message": error_message or "Une erreur s'est produite lors du test",
                "p_value": None,
                "test_status": "error",
                "test_name": self.test_name
            }

        response = {
            "error": False,
            "p_value": p_value,
            "test_status": test_status,
            "message": TestStatusDeterminer.get_status_message(test_status),
            "test_name": self.test_name,
        }

        # Ajouter les informations supplémentaires si elles existent
        if additional_info:
            response["additional_info"] = additional_info

        return response
