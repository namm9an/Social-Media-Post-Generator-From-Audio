#!/usr/bin/env python3
"""
FLAN-T5 Text Generation Service

Enterprise-grade implementation of FLAN-T5 for social media post generation.
Handles model loading, text generation, and error management.
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers.utils import logging as transformers_logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress verbose transformers logging
transformers_logging.set_verbosity_error()

@dataclass
class GenerationConfig:
    """Configuration for text generation parameters"""
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    early_stopping: bool = True
    pad_token_id: int = 0
    eos_token_id: int = 1

class ModelLoadingError(Exception):
    """Custom exception for model loading failures"""
    pass

class TextGenerationError(Exception):
    """Custom exception for text generation failures"""
    pass

class FlanT5Service:
    """
    FLAN-T5 text generation service with enterprise-level features:
    - Thread-safe model loading and generation
    - GPU/CPU automatic detection
    - Comprehensive error handling
    - Performance monitoring
    - Resource management
    """
    
    def __init__(self, model_name: str = "google/flan-t5-large"):
        """
        Initialize the FLAN-T5 service
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = None
        self.generation_config = GenerationConfig()
        self._loading_lock = threading.Lock()
        self._model_loaded = False
        
        # Performance tracking
        self.generation_stats = {
            'total_generations': 0,
            'total_time': 0.0,
            'average_time': 0.0,
            'errors': 0
        }
        
        logger.info(f"Initialized FLAN-T5 service with model: {model_name}")
    
    def _detect_device(self) -> str:
        """
        Detect the best available device for model execution
        
        Returns:
            Device string ('cuda', 'mps', or 'cpu')
        """
        try:
            if torch.cuda.is_available():
                device = "cuda"
                logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
                logger.info("Using MPS (Metal Performance Shaders) device")
            else:
                device = "cpu"
                logger.info("Using CPU device")
            
            return device
        except Exception as e:
            logger.warning(f"Error detecting device: {e}. Falling back to CPU.")
            return "cpu"
    
    def load_model(self) -> Dict[str, Any]:
        """
        Load the FLAN-T5 model and tokenizer with thread safety
        
        Returns:
            Dictionary with loading status and information
        """
        with self._loading_lock:
            if self._model_loaded:
                return {
                    'status': 'already_loaded',
                    'model_name': self.model_name,
                    'device': str(self.device)
                }
            
            try:
                start_time = time.time()
                logger.info(f"Loading FLAN-T5 model: {self.model_name}")
                
                # Detect device
                self.device = self._detect_device()
                
                # Load tokenizer
                logger.info("Loading tokenizer...")
                self.tokenizer = T5Tokenizer.from_pretrained(
                    self.model_name,
                    model_max_length=512,
                    padding_side='left'
                )
                
                # Set pad token if not set
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Load model
                logger.info("Loading model...")
                if self.device == 'cuda':
                    self.model = T5ForConditionalGeneration.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        low_cpu_mem_usage=True
                    )
                else:
                    # For CPU, don't use device_map or low_cpu_mem_usage
                    self.model = T5ForConditionalGeneration.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float32
                    )
                
                # Move model to device if not using device_map
                if self.device != 'cuda' or not hasattr(self.model, 'hf_device_map'):
                    self.model = self.model.to(self.device)
                
                # Set model to evaluation mode
                self.model.eval()
                
                # Update generation config with tokenizer info
                self.generation_config.pad_token_id = self.tokenizer.pad_token_id
                self.generation_config.eos_token_id = self.tokenizer.eos_token_id
                
                load_time = time.time() - start_time
                self._model_loaded = True
                
                logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
                
                return {
                    'status': 'loaded',
                    'model_name': self.model_name,
                    'device': str(self.device),
                    'load_time': load_time,
                    'model_size': f"{sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M parameters"
                }
                
            except Exception as e:
                error_msg = f"Failed to load model {self.model_name}: {str(e)}"
                logger.error(error_msg)
                raise ModelLoadingError(error_msg)
    
    def _validate_input(self, prompt: str) -> str:
        """
        Validate and sanitize input prompt
        
        Args:
            prompt: Input text prompt
            
        Returns:
            Sanitized prompt
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Remove excessive whitespace
        prompt = ' '.join(prompt.split())
        
        # Limit prompt length to prevent memory issues
        max_prompt_length = 1000
        if len(prompt) > max_prompt_length:
            prompt = prompt[:max_prompt_length]
            logger.warning(f"Prompt truncated to {max_prompt_length} characters")
        
        return prompt
    
    def _post_process_output(self, generated_text: str) -> str:
        """
        Post-process generated text for quality and consistency
        
        Args:
            generated_text: Raw generated text
            
        Returns:
            Cleaned and formatted text
        """
        if not generated_text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(generated_text.split())
        
        # Remove common artifacts
        artifacts = [
            '<pad>', '</s>', '<s>', '<unk>',
            'Question:', 'Answer:', 'Context:',
            'Generate:', 'Create:', 'Write:'
        ]
        
        for artifact in artifacts:
            text = text.replace(artifact, '').strip()
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            # Add period if it doesn't end with punctuation
            if not text.endswith((':', ';', ',')):
                text += '.'
        
        return text.strip()
    
    @contextmanager
    def _generation_context(self):
        """Context manager for generation with error handling and cleanup"""
        try:
            if not self._model_loaded:
                raise TextGenerationError("Model not loaded. Call load_model() first.")
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Disable gradient computation
            with torch.no_grad():
                yield
                
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise TextGenerationError(f"Generation failed: {str(e)}")
    
    def generate_text(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using FLAN-T5 model
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        start_time = time.time()
        
        try:
            # Validate input
            prompt = self._validate_input(prompt)
            
            # Update generation config with provided parameters
            config = self.generation_config
            if max_length is not None:
                config.max_length = max_length
            if temperature is not None:
                config.temperature = temperature
            if top_p is not None:
                config.top_p = top_p
            
            # Update config with additional kwargs
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            with self._generation_context():
                # Tokenize input
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # Generate text
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_length=config.max_length,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    do_sample=config.do_sample,
                    num_return_sequences=config.num_return_sequences,
                    repetition_penalty=config.repetition_penalty,
                    length_penalty=config.length_penalty,
                    early_stopping=config.early_stopping,
                    pad_token_id=config.pad_token_id,
                    eos_token_id=config.eos_token_id
                )
                
                # Decode generated text
                generated_text = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True
                )
                
                # Post-process output
                generated_text = self._post_process_output(generated_text)
                
                generation_time = time.time() - start_time
                
                # Update statistics
                self.generation_stats['total_generations'] += 1
                self.generation_stats['total_time'] += generation_time
                self.generation_stats['average_time'] = (
                    self.generation_stats['total_time'] / 
                    self.generation_stats['total_generations']
                )
                
                logger.info(f"Generated text in {generation_time:.2f} seconds")
                
                return {
                    'text': generated_text,
                    'generation_time': generation_time,
                    'prompt': prompt,
                    'config': {
                        'max_length': config.max_length,
                        'temperature': config.temperature,
                        'top_p': config.top_p
                    },
                    'metadata': {
                        'model': self.model_name,
                        'device': str(self.device),
                        'timestamp': time.time()
                    }
                }
                
        except Exception as e:
            error_msg = f"Text generation failed: {str(e)}"
            logger.error(error_msg)
            raise TextGenerationError(error_msg)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'model_loaded': self._model_loaded,
            'device': str(self.device) if self.device else None,
            'generation_stats': self.generation_stats.copy()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the service
        
        Returns:
            Dictionary with health status
        """
        try:
            if not self._model_loaded:
                return {
                    'status': 'unhealthy',
                    'reason': 'Model not loaded'
                }
            
            # Test generation with simple prompt
            test_result = self.generate_text(
                "Generate a simple greeting:",
                max_length=50,
                temperature=0.5
            )
            
            return {
                'status': 'healthy',
                'model_loaded': True,
                'test_generation_time': test_result['generation_time'],
                'stats': self.generation_stats.copy()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'reason': str(e)
            }
    
    def aggressive_cleanup(self):
        """Aggressive memory cleanup for memory management"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("Aggressive memory cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during aggressive cleanup: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
            
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            # Aggressive cleanup
            self.aggressive_cleanup()
            
            self._model_loaded = False
            logger.info("FLAN-T5 service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global service instance
flan_t5_service = FlanT5Service()
