"""
Memory optimization configuration to reduce memory pressure during transcription.
"""

import gc
import logging
import psutil
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Optimize memory usage for AI model operations."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def force_garbage_collection(self):
        """Force aggressive garbage collection."""
        collected = 0
        for i in range(3):
            collected += gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
        return collected
    
    def optimize_for_transcription(self):
        """Optimize memory before transcription."""
        initial_memory = self.get_memory_usage()
        
        # Force garbage collection
        self.force_garbage_collection()
        
        # Set low priority for current process
        try:
            self.process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)
        except (psutil.AccessDenied, AttributeError):
            pass
        
        final_memory = self.get_memory_usage()
        logger.info(f"Memory optimization: {initial_memory:.1f}MB -> {final_memory:.1f}MB")
        
        return {
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_saved_mb': initial_memory - final_memory
        }
    
    @contextmanager
    def memory_managed_operation(self, operation_name="operation"):
        """Context manager for memory-managed operations."""
        logger.info(f"[MEMORY] Starting {operation_name}")
        start_memory = self.get_memory_usage()
        
        try:
            # Optimize before operation
            self.force_garbage_collection()
            yield
        finally:
            # Clean up after operation
            self.force_garbage_collection()
            end_memory = self.get_memory_usage()
            memory_delta = end_memory - start_memory
            logger.info(f"[MEMORY] {operation_name} completed. Memory delta: {memory_delta:+.1f}MB")

# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()
