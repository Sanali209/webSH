"""Configuration for Deduplicator Plugin."""
from pydantic import BaseModel, Field
from core.sdk import PluginSettings
from typing import List


class DeduplicatorSettings(PluginSettings):
    """Settings for the Deduplicator plugin."""
    
    # Hash types to use
    use_md5: bool = Field(
        default=True,
        description="Use MD5 hashing for exact content matching"
    )
    
    use_perceptual_hash: bool = Field(
        default=True,
        description="Use perceptual hashing for image similarity"
    )
    
    # Performance settings
    min_file_size: int = Field(
        default=1,
        description="Minimum file size in bytes to consider for deduplication (skip empty files)"
    )
    
    max_file_size: int = Field(
        default=100 * 1024 * 1024,  # 100 MB
        description="Maximum file size in bytes to hash (prevent memory issues)"
    )
    
    # Image perceptual hash settings
    perceptual_hash_types: List[str] = Field(
        default=["phash", "dhash"],
        description="Types of perceptual hashes to use (phash, dhash, ahash, whash)"
    )
    
    similarity_threshold: float = Field(
        default=0.95,
        description="Similarity threshold for perceptual hashes (0.0-1.0)"
    )
    
    # File types to process
    image_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        description="Image file extensions to process with perceptual hashing"
    )
    
    # Scanning settings
    auto_scan_on_load: bool = Field(
        default=False,
        description="Automatically scan for duplicates when plugin loads"
    )
