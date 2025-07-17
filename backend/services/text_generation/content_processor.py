import re
import json
from typing import List

CHARACTER_LIMITS = {
    'linkedin': 3000,
    'twitter': 280,
    'instagram': 2200
}

class ContentProcessor:
    """
    Processes and formats generated content for various social media platforms.
    """

    @staticmethod
    def format_for_platform(text: str, platform: str) -> str:
        """
        Apply platform-specific formatting to text.

        Args:
            text: The generated text content.
            platform: The target social media platform.

        Returns:
            Formatted text for the specified platform.
        """
        if platform in CHARACTER_LIMITS:
            return text[:CHARACTER_LIMITS[platform]]
        return text

    @staticmethod
    def validate_character_limits(text: str, platform: str) -> bool:
        """
        Validate that the text adheres to character limits for the platform.

        Args:
            text: The text to validate.
            platform: The social media platform.

        Returns:
            Boolean indicating whether the text is valid.
        """
        return len(text) <= CHARACTER_LIMITS.get(platform, len(text))

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """
        Extract hashtags from the text.

        Args:
            text: The text to extract hashtags from.

        Returns:
            List of hashtags.
        """
        return re.findall(r"#\w+", text)

    @staticmethod
    def add_emojis(text: str, platform: str) -> str:
        """
        Add appropriate emojis to text based on platform.

        Args:
            text: The text to which emojis will be added.
            platform: The social media platform.

        Returns:
            Text with added emojis.
        """
        # Simple example, could be expanded for context-specific emojis
        if platform == 'instagram':
            return text + ' 😊'
        return text

    @staticmethod
    def clean_generated_text(text: str) -> str:
        """
        Remove artifacts and clean the generated text output.

        Args:
            text: The generated text to clean.

        Returns:
            Cleaned text.
        """
        artifacts = ["&lt;&gt;", "<eos>", "#%^&*"]  # Placeholder artifacts, customize as needed
        for artifact in artifacts:
            text = text.replace(artifact, " ")
        return ' '.join(text.split())
