import keyring
from typing import Optional
from loguru import logger

SERVICE_NAME = "advanced-claude-proxy"

class SecretVault:
    """Manages sensitive credentials using the OS keyring."""

    @staticmethod
    def set_secret(key: str, value: str) -> None:
        try:
            keyring.set_password(SERVICE_NAME, key, value)
            logger.debug(f"Secret '{key}' stored securely.")
        except Exception as e:
            logger.error(f"Failed to store secret '{key}': {e}")
            raise

    @staticmethod
    def get_secret(key: str) -> Optional[str]:
        try:
            return keyring.get_password(SERVICE_NAME, key)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{key}': {e}")
            return None

    @staticmethod
    def delete_secret(key: str) -> None:
        try:
            keyring.delete_password(SERVICE_NAME, key)
            logger.debug(f"Secret '{key}' deleted securely.")
        except keyring.errors.PasswordDeleteError:
            pass
        except Exception as e:
            logger.error(f"Failed to delete secret '{key}': {e}")
