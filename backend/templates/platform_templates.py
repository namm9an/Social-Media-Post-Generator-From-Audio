# Platform Templates for Social Media Post Generation

PLATFORM_TEMPLATES = {
    "linkedin": {
        "professional": "Create a professional LinkedIn post about: {content}. Use business language, include insights, and add 2-3 relevant hashtags. Keep it engaging and valuable.",
        "casual": "Write a casual but professional LinkedIn update about: {content}. Use friendly tone, personal touches, and 2-3 hashtags. Make it conversational.",
        "witty": "Create an engaging LinkedIn post with personality about: {content}. Add humor where appropriate, keep it professional, and include 2-3 hashtags.",
        "motivational": "Write an inspiring LinkedIn post about: {content}. Use motivational language, call-to-action, and 2-3 hashtags. Make it uplifting."
    },
    "twitter": {
        "professional": "Create a professional tweet about: {content}. Keep under 280 characters, use 1-2 hashtags, make it concise and valuable.",
        "casual": "Write a casual tweet about: {content}. Keep under 280 characters, use friendly tone, 1-2 hashtags, make it conversational.",
        "witty": "Create a witty tweet about: {content}. Keep under 280 characters, add humor, use 1-2 hashtags, make it engaging.",
        "motivational": "Write an inspiring tweet about: {content}. Keep under 280 characters, use motivational tone, 1-2 hashtags, include call-to-action."
    },
    "instagram": {
        "professional": "Create a professional Instagram caption about: {content}. Use storytelling, include emojis, add 5-7 hashtags, make it engaging.",
        "casual": "Write a casual Instagram caption about: {content}. Use friendly tone, include emojis, add 5-7 hashtags, make it personal.",
        "witty": "Create an engaging Instagram caption about: {content}. Add humor, use emojis, include 5-7 hashtags, make it fun.",
        "motivational": "Write an inspiring Instagram caption about: {content}. Use motivational tone, emojis, 5-7 hashtags, include call-to-action."
    }
}

def get_template(platform: str, tone: str) -> str:
    """
    Retrieve the template for a specific platform and tone.

    Args:
        platform: The social media platform (e.g., 'linkedin', 'twitter', 'instagram')
        tone: The tone of the post (e.g., 'professional', 'casual', 'witty', 'motivational')

    Returns:
        The template string to use for generation.

    Raises:
        ValueError: If the platform or tone is not recognized.
    """
    try:
        return PLATFORM_TEMPLATES[platform][tone]
    except KeyError as e:
        raise ValueError(f"Template not found for platform {platform} with tone {tone}: {e}")
