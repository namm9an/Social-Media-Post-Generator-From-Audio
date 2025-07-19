#!/usr/bin/env python3
"""
Advanced Social Media Post Generation Service

Modern implementation with comprehensive tone support, memory management,
and improved text generation quality.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import signal

from .flan_t5_service import flan_t5_service, TextGenerationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostTone(Enum):
    """Available tones for social media posts"""
    WITTY = "witty"
    PROFESSIONAL = "professional" 
    MOTIVATIONAL = "motivational"
    CASUAL = "casual"
    EDUCATIONAL = "educational"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    URGENT = "urgent"

@dataclass
class PostGenerationConfig:
    """Configuration for post generation"""
    tone: PostTone = PostTone.PROFESSIONAL
    max_length: int = 280
    min_length: int = 50
    include_hashtags: bool = True
    include_emojis: bool = True
    platform_specific: bool = False
    target_audience: Optional[str] = None
    key_points: List[str] = None
    call_to_action: bool = False
    generation_timeout: int = 30

class PostGenerationTimeout(Exception):
    """Exception for generation timeout"""
    pass

class PostGenerator:
    """
    Advanced social media post generator with tone support and memory management
    """
    
    def __init__(self):
        """Initialize the post generator"""
        self.tone_prompts = self._initialize_tone_prompts()
        self.generation_stats = {
            'total_generated': 0,
            'successful': 0,
            'failed': 0,
            'timeout': 0,
            'average_generation_time': 0.0
        }
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def _initialize_tone_prompts(self) -> Dict[PostTone, str]:
        """Initialize tone-specific prompts for better generation"""
        return {
            PostTone.WITTY: """
Create a witty and clever social media post from this content. Use humor, wordplay, 
and smart observations. Keep it engaging and shareable. Make it sound natural and conversational.
Content: {content}
Post:""",
            
            PostTone.PROFESSIONAL: """
Create a professional social media post from this content. Use clear, authoritative language.
Focus on key insights and valuable information. Keep it polished and credible.
Content: {content}
Professional post:""",
            
            PostTone.MOTIVATIONAL: """
Create an inspiring and motivational social media post from this content. Use uplifting language,
encourage action, and inspire your audience. Make it energetic and empowering.
Content: {content}
Motivational post:""",
            
            PostTone.CASUAL: """
Create a casual, friendly social media post from this content. Use conversational language,
be relatable and approachable. Make it feel like talking to a friend.
Content: {content}
Casual post:""",
            
            PostTone.EDUCATIONAL: """
Create an educational social media post from this content. Focus on teaching and informing.
Use clear explanations and highlight key learning points. Make it informative yet engaging.
Content: {content}
Educational post:""",
            
            PostTone.HUMOROUS: """
Create a funny and entertaining social media post from this content. Use humor, jokes,
and entertaining observations. Make people smile or laugh while sharing the message.
Content: {content}
Funny post:""",
            
            PostTone.INSPIRATIONAL: """
Create an inspirational social media post from this content. Focus on hope, dreams,
and positive transformation. Use uplifting and encouraging language.
Content: {content}
Inspirational post:""",
            
            PostTone.URGENT: """
Create an urgent, action-oriented social media post from this content. Create a sense
of importance and immediacy. Use compelling language that motivates quick action.
Content: {content}
Urgent post:"""
        }
    
    def _timeout_handler(self, signum, frame):
        """Handle timeout signal"""
        raise PostGenerationTimeout("Post generation timed out")
    
    def _generate_with_timeout(self, prompt: str, config: PostGenerationConfig) -> str:
        """Generate text with timeout protection"""
        
        def generate_text():
            return flan_t5_service.generate_text(
                prompt=prompt,
                max_length=config.max_length,
                temperature=0.8,
                top_p=0.9,
                do_sample=True
            )
        
        # Use ThreadPoolExecutor for timeout control
        future = self.executor.submit(generate_text)
        
        try:
            result = future.result(timeout=config.generation_timeout)
            return result['text']
        except TimeoutError:
            future.cancel()
            self.generation_stats['timeout'] += 1
            raise PostGenerationTimeout(f"Generation timed out after {config.generation_timeout} seconds")
    
    def _enhance_prompt_with_context(self, base_prompt: str, config: PostGenerationConfig) -> str:
        """Enhance prompt with additional context and requirements"""
        enhancements = []
        
        if config.include_hashtags:
            enhancements.append("Include relevant hashtags.")
        
        if config.include_emojis and config.tone in [PostTone.CASUAL, PostTone.HUMOROUS, PostTone.MOTIVATIONAL]:
            enhancements.append("Use appropriate emojis.")
        
        if config.call_to_action:
            enhancements.append("End with a clear call-to-action.")
        
        if config.target_audience:
            enhancements.append(f"Target audience: {config.target_audience}.")
        
        if config.key_points:
            key_points_str = ", ".join(config.key_points)
            enhancements.append(f"Key points to include: {key_points_str}.")
        
        if enhancements:
            enhanced_prompt = base_prompt + " " + " ".join(enhancements)
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt
    
    def _post_process_generated_text(self, text: str, config: PostGenerationConfig) -> str:
        """Post-process generated text for quality and length"""
        if not text:
            return text
        
        # Remove redundant phrases
        redundant_phrases = [
            "Here's a", "Here is a", "This is a", "Check out this",
            "In this post", "This post", "Social media post:",
            "Post:", "Tweet:", "Facebook post:", "Instagram post:"
        ]
        
        processed_text = text
        for phrase in redundant_phrases:
            processed_text = processed_text.replace(phrase, "").strip()
        
        # Ensure proper capitalization
        if processed_text and not processed_text[0].isupper():
            processed_text = processed_text[0].upper() + processed_text[1:]
        
        # Trim to max length while preserving word boundaries
        if len(processed_text) > config.max_length:
            words = processed_text.split()
            result = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= config.max_length:
                    result.append(word)
                    current_length += len(word) + 1
                else:
                    break
            
            processed_text = " ".join(result)
            if not processed_text.endswith(('.', '!', '?')):
                processed_text += "..."
        
        # Ensure minimum length
        if len(processed_text) < config.min_length:
            logger.warning(f"Generated text too short ({len(processed_text)} chars), may need regeneration")
        
        return processed_text.strip()
    
    def generate_post(
        self,
        content: str,
        config: Optional[PostGenerationConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate a social media post with specified tone and configuration
        
        Args:
            content: Source content to create post from
            config: Generation configuration
            
        Returns:
            Dictionary with generated post and metadata
        """
        if config is None:
            config = PostGenerationConfig()
        
        start_time = time.time()
        
        try:
            # Validate input
            if not content or not content.strip():
                raise ValueError("Content cannot be empty")
            
            # Clean and truncate content if necessary
            content = content.strip()
            if len(content) > 2000:
                content = content[:2000] + "..."
                logger.warning("Content truncated to 2000 characters")
            
            # Get tone-specific prompt
            base_prompt = self.tone_prompts[config.tone].format(content=content)
            
            # Enhance prompt with additional context
            enhanced_prompt = self._enhance_prompt_with_context(base_prompt, config)
            
            logger.info(f"Generating post with tone: {config.tone.value}")
            
            # Generate text with timeout protection
            generated_text = self._generate_with_timeout(enhanced_prompt, config)
            
            # Post-process the generated text
            final_post = self._post_process_generated_text(generated_text, config)
            
            generation_time = time.time() - start_time
            
            # Update statistics
            self.generation_stats['total_generated'] += 1
            self.generation_stats['successful'] += 1
            
            # Update average generation time
            total_time = self.generation_stats['average_generation_time'] * (self.generation_stats['total_generated'] - 1)
            self.generation_stats['average_generation_time'] = (total_time + generation_time) / self.generation_stats['total_generated']
            
            logger.info(f"Post generated successfully in {generation_time:.2f} seconds")
            
            return {
                'post': final_post,
                'tone': config.tone.value,
                'generation_time': generation_time,
                'word_count': len(final_post.split()),
                'character_count': len(final_post),
                'config': {
                    'tone': config.tone.value,
                    'max_length': config.max_length,
                    'include_hashtags': config.include_hashtags,
                    'include_emojis': config.include_emojis,
                    'call_to_action': config.call_to_action
                },
                'metadata': {
                    'content_length': len(content),
                    'prompt_used': enhanced_prompt[:100] + "..." if len(enhanced_prompt) > 100 else enhanced_prompt,
                    'generation_successful': True,
                    'timestamp': time.time()
                },
                'status': 'success'
            }
            
        except PostGenerationTimeout as e:
            self.generation_stats['total_generated'] += 1
            self.generation_stats['timeout'] += 1
            logger.error(f"Post generation timeout: {e}")
            
            return {
                'post': '',
                'error': str(e),
                'status': 'timeout',
                'generation_time': time.time() - start_time
            }
            
        except Exception as e:
            self.generation_stats['total_generated'] += 1
            self.generation_stats['failed'] += 1
            logger.error(f"Post generation failed: {e}")
            
            return {
                'post': '',
                'error': str(e),
                'status': 'failed',
                'generation_time': time.time() - start_time
            }
    
    def generate_multiple_posts(
        self,
        content: str,
        tones: List[PostTone],
        base_config: Optional[PostGenerationConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple posts with different tones
        
        Args:
            content: Source content
            tones: List of tones to generate
            base_config: Base configuration to use
            
        Returns:
            List of generated posts
        """
        results = []
        
        for tone in tones:
            config = base_config or PostGenerationConfig()
            config.tone = tone
            
            try:
                result = self.generate_post(content, config)
                results.append(result)
                
                # Add small delay between generations to prevent resource conflicts
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate post with tone {tone.value}: {e}")
                results.append({
                    'post': '',
                    'tone': tone.value,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.generation_stats.copy()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.executor.shutdown(wait=True)
            logger.info("PostGenerator cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during PostGenerator cleanup: {e}")

# Global post generator instance
post_generator = PostGenerator()
