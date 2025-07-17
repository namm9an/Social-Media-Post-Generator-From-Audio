"""
Text generation functionality using local FLAN-T5 model
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

class TextGenerator:
    def __init__(self, model_name="google/flan-t5-large"):
        """Initialize FLAN-T5 model."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load FLAN-T5 model and tokenizer."""
        if self.model is None:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        return self.model, self.tokenizer
    
    def generate_post(self, text, platform="linkedin", tone="professional"):
        """Generate social media post from text."""
        model, tokenizer = self.load_model()
        
        # Platform-specific prompts for FLAN-T5
        prompts = {
            "linkedin": f"Create a professional LinkedIn post about: {text}. Make it engaging and professional.",
            "twitter": f"Create a short Twitter post about: {text}. Keep it under 280 characters.",
            "instagram": f"Create an engaging Instagram caption about: {text}. Make it visual and engaging."
        }
        
        # Tone modifications
        tone_modifiers = {
            "professional": "Use formal business language and professional tone.",
            "casual": "Use friendly, conversational language and casual tone.",
            "witty": "Use humor and wit while being engaging."
        }
        
        prompt = f"{prompts.get(platform, prompts['linkedin'])} {tone_modifiers.get(tone, '')}"
        
        # Generate text with FLAN-T5
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated_text.strip()

# Test function
def test_flan_t5():
    """Test FLAN-T5 model loading."""
    try:
        generator = TextGenerator()
        generator.load_model()
        print("✓ FLAN-T5 model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ FLAN-T5 model loading failed: {e}")
        return False

if __name__ == "__main__":
    test_flan_t5()
