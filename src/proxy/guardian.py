from loguru import logger

class ConstitutionalGuardian:
    """Filters commands and prompts to prevent malicious behavior."""

    DANGEROUS_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        "chmod -R 777 /",
        ":(){ :|:& };:", # Fork bomb
    ]

    @classmethod
    def check_command(cls, command: str) -> bool:
        """
        Returns True if the command is considered safe, False otherwise.
        In a real implementation, this could call a smaller LLM for semantic checking.
        """
        cmd_lower = command.lower()
        for dangerous in cls.DANGEROUS_COMMANDS:
            if dangerous in cmd_lower:
                logger.warning(f"Guardian blocked malicious command: {command}")
                return False
        return True

    @classmethod
    def check_prompt(cls, prompt: str) -> bool:
        """
        Returns True if the prompt is safe.
        """
        if "ignore all previous instructions" in prompt.lower():
            logger.warning("Guardian blocked potential prompt injection.")
            return False
        return True
