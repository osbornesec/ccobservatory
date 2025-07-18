"""
Message compression for WebSocket broadcasting.

This module provides message compression functionality for WebSocket communications,
reducing bandwidth usage for large payloads while maintaining efficiency.
"""

import zlib


class MessageCompressor:
    """Message compressor for WebSocket broadcasting"""
    
    def __init__(self, compression_level: int = 6, min_size_for_compression: int = 1024, 
                 min_compression_ratio: float = 0.1):
        self.compression_level = compression_level
        self.min_size_for_compression = min_size_for_compression
        self.min_compression_ratio = min_compression_ratio
    
    def compress(self, message: str) -> bytes:
        """Compress message using zlib"""
        try:
            return zlib.compress(message.encode(), self.compression_level)
        except zlib.error as e:
            logger.error(f"Compression failed: {e}")
            return message.encode()  # Return uncompressed as fallback

    def decompress(self, compressed_data: bytes) -> str:
        """Decompress message using zlib"""
        try:
            return zlib.decompress(compressed_data).decode()
        except (zlib.error, UnicodeDecodeError) as e:
            logger.error(f"Decompression failed: {e}")
            raise ValueError("Invalid compressed data") from e
    
    def calculate_compression_ratio(self, original: str, compressed: bytes) -> float:
        """Calculate compression ratio"""
        original_size = len(original.encode())
        compressed_size = len(compressed)
        return (original_size - compressed_size) / original_size
    
    def compress_if_beneficial(self, message: str) -> bytes:
        """Compress only if beneficial"""
        message_bytes = message.encode()
        
        # Skip compression for small messages
        if len(message_bytes) < self.min_size_for_compression:
            return message_bytes
        
        # Try compression
        compressed = self.compress(message)
        ratio = self.calculate_compression_ratio(message, compressed)
        
        # Use compression only if beneficial
        if ratio >= self.min_compression_ratio:
            return compressed
        return message_bytes