"""Deduplicator Plugin Backend - Find duplicate files using hashing."""
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from PIL import Image
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False

from core.sdk import PluginBase, PluginContext
from .config import DeduplicatorSettings

logger = logging.getLogger(__name__)


# Request/Response models
class HashRequest(BaseModel):
    """Request model for hashing a single file."""
    file_path: str
    hash_types: Optional[List[str]] = ["md5"]


class HashResponse(BaseModel):
    """Response model for hash calculation."""
    file_path: str
    hashes: Dict[str, str]
    file_size: int


class ScanRequest(BaseModel):
    """Request model for scanning directories."""
    paths: List[str]
    recursive: bool = True


class ScanResponse(BaseModel):
    """Response model for scan operation."""
    scanned: int
    hashed: int
    duplicates_found: int
    errors: int


class DuplicateGroup(BaseModel):
    """Model for a group of duplicate files."""
    hash: str
    hash_type: str
    files: List[str]
    file_size: int
    count: int


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection."""
    duplicate_groups: List[DuplicateGroup]
    total_duplicates: int
    total_groups: int
    space_wasted: int  # Total bytes that could be saved


class HashService:
    """
    Service for calculating file hashes.
    
    Supports MD5 for exact matching and perceptual hashing for images.
    """
    
    def __init__(self, settings: DeduplicatorSettings):
        self.settings = settings
        
        if not IMAGEHASH_AVAILABLE and settings.use_perceptual_hash:
            logger.warning("imagehash library not available, perceptual hashing disabled")
            self.settings.use_perceptual_hash = False
    
    def calculate_md5(self, file_path: str) -> Optional[str]:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash as hex string, or None on error
        """
        try:
            md5_hash = hashlib.md5()
            
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    md5_hash.update(chunk)
            
            return md5_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {e}")
            return None
    
    def calculate_perceptual_hash(self, file_path: str, hash_type: str = "phash") -> Optional[str]:
        """
        Calculate perceptual hash of an image.
        
        Args:
            file_path: Path to the image file
            hash_type: Type of perceptual hash (phash, dhash, ahash, whash)
            
        Returns:
            Perceptual hash as hex string, or None on error
        """
        if not IMAGEHASH_AVAILABLE:
            return None
        
        try:
            image = Image.open(file_path)
            
            # Calculate hash based on type
            if hash_type == "phash":
                img_hash = imagehash.phash(image)
            elif hash_type == "dhash":
                img_hash = imagehash.dhash(image)
            elif hash_type == "ahash":
                img_hash = imagehash.average_hash(image)
            elif hash_type == "whash":
                img_hash = imagehash.whash(image)
            else:
                logger.warning(f"Unknown hash type: {hash_type}, using phash")
                img_hash = imagehash.phash(image)
            
            return str(img_hash)
        except Exception as e:
            logger.error(f"Error calculating {hash_type} for {file_path}: {e}")
            return None
    
    def hash_file(self, file_path: str, hash_types: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Calculate all requested hashes for a file.
        
        Args:
            file_path: Path to the file
            hash_types: List of hash types to calculate (md5, phash, dhash, etc.)
            
        Returns:
            Dictionary mapping hash type to hash value
        """
        if hash_types is None:
            hash_types = ["md5"]
            if self.settings.use_perceptual_hash:
                hash_types.extend(self.settings.perceptual_hash_types)
        
        hashes = {}
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size < self.settings.min_file_size:
                logger.debug(f"File too small: {file_path} ({file_size} bytes)")
                return hashes
            if file_size > self.settings.max_file_size:
                logger.warning(f"File too large: {file_path} ({file_size} bytes), skipping")
                return hashes
        except Exception as e:
            logger.error(f"Error checking file size for {file_path}: {e}")
            return hashes
        
        # Calculate MD5 hash
        if "md5" in hash_types and self.settings.use_md5:
            md5_hash = self.calculate_md5(file_path)
            if md5_hash:
                hashes["md5"] = md5_hash
        
        # Calculate perceptual hashes for images
        if self.settings.use_perceptual_hash:
            file_ext = Path(file_path).suffix.lower()
            if file_ext in self.settings.image_extensions:
                for hash_type in self.settings.perceptual_hash_types:
                    if hash_type in hash_types:
                        perceptual_hash = self.calculate_perceptual_hash(file_path, hash_type)
                        if perceptual_hash:
                            hashes[hash_type] = perceptual_hash
        
        return hashes
    
    def is_image(self, file_path: str) -> bool:
        """Check if a file is an image based on extension."""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.settings.image_extensions


class DeduplicatorPlugin(PluginBase):
    """
    Deduplicator Plugin.
    
    Identifies duplicate files using content hashing and perceptual image matching.
    """
    
    def __init__(self):
        self.settings = DeduplicatorSettings()
        self.hash_service: Optional[HashService] = None
        self.router = APIRouter()
        
        # In-memory hash storage (in production, would use LanceDB)
        self._hash_db: Dict[str, Dict[str, str]] = {}  # {file_path: {hash_type: hash_value}}
        self._file_sizes: Dict[str, int] = {}  # {file_path: size}
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for the deduplicator."""
        
        @self.router.post("/hash", response_model=HashResponse)
        async def hash_file(request: HashRequest):
            """
            Calculate hash for a single file.
            
            Example:
                POST /api/plugins/deduplicator/hash
                {"file_path": "/path/to/file.txt", "hash_types": ["md5"]}
            """
            if not self.hash_service:
                raise HTTPException(status_code=503, detail="Hash service not initialized")
            
            if not os.path.exists(request.file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
            
            try:
                hashes = self.hash_service.hash_file(request.file_path, request.hash_types)
                file_size = os.path.getsize(request.file_path)
                
                # Store in memory
                self._hash_db[request.file_path] = hashes
                self._file_sizes[request.file_path] = file_size
                
                return HashResponse(
                    file_path=request.file_path,
                    hashes=hashes,
                    file_size=file_size
                )
            except Exception as e:
                logger.error(f"Error hashing file {request.file_path}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/scan", response_model=ScanResponse)
        async def scan_directories(request: ScanRequest):
            """
            Scan directories and calculate hashes for all files.
            
            Example:
                POST /api/plugins/deduplicator/scan
                {"paths": ["/path/to/dir"], "recursive": true}
            """
            if not self.hash_service:
                raise HTTPException(status_code=503, detail="Hash service not initialized")
            
            scanned = 0
            hashed = 0
            errors = 0
            
            for path in request.paths:
                if not os.path.exists(path):
                    logger.warning(f"Path not found: {path}")
                    errors += 1
                    continue
                
                if os.path.isfile(path):
                    # Single file
                    try:
                        hashes = self.hash_service.hash_file(path)
                        if hashes:
                            self._hash_db[path] = hashes
                            self._file_sizes[path] = os.path.getsize(path)
                            hashed += 1
                        scanned += 1
                    except Exception as e:
                        logger.error(f"Error processing file {path}: {e}")
                        errors += 1
                else:
                    # Directory
                    if request.recursive:
                        pattern = "**/*"
                    else:
                        pattern = "*"
                    
                    for file_path in Path(path).glob(pattern):
                        if file_path.is_file():
                            scanned += 1
                            try:
                                hashes = self.hash_service.hash_file(str(file_path))
                                if hashes:
                                    self._hash_db[str(file_path)] = hashes
                                    self._file_sizes[str(file_path)] = os.path.getsize(str(file_path))
                                    hashed += 1
                            except Exception as e:
                                logger.error(f"Error processing file {file_path}: {e}")
                                errors += 1
            
            # Find duplicates
            duplicates = self._find_duplicates()
            
            return ScanResponse(
                scanned=scanned,
                hashed=hashed,
                duplicates_found=len(duplicates),
                errors=errors
            )
        
        @self.router.get("/duplicates", response_model=DuplicatesResponse)
        async def get_duplicates():
            """
            Find and return all duplicate file groups.
            
            Example:
                GET /api/plugins/deduplicator/duplicates
            """
            if not self.hash_service:
                raise HTTPException(status_code=503, detail="Hash service not initialized")
            
            duplicate_groups = self._find_duplicates()
            
            total_duplicates = sum(group.count - 1 for group in duplicate_groups)  # -1 because we keep one copy
            space_wasted = sum(group.file_size * (group.count - 1) for group in duplicate_groups)
            
            return DuplicatesResponse(
                duplicate_groups=duplicate_groups,
                total_duplicates=total_duplicates,
                total_groups=len(duplicate_groups),
                space_wasted=space_wasted
            )
        
        @self.router.get("/duplicates/{file_path:path}", response_model=List[str])
        async def find_duplicates_of_file(file_path: str):
            """
            Find duplicates of a specific file.
            
            Example:
                GET /api/plugins/deduplicator/duplicates/path/to/file.txt
            """
            if not self.hash_service:
                raise HTTPException(status_code=503, detail="Hash service not initialized")
            
            if file_path not in self._hash_db:
                raise HTTPException(status_code=404, detail="File not in hash database. Run scan first.")
            
            file_hashes = self._hash_db[file_path]
            duplicates = []
            
            # Find files with matching hashes
            for other_path, other_hashes in self._hash_db.items():
                if other_path == file_path:
                    continue
                
                # Check if any hash matches
                for hash_type, hash_value in file_hashes.items():
                    if other_hashes.get(hash_type) == hash_value:
                        duplicates.append(other_path)
                        break
            
            return duplicates
        
        @self.router.get("/info")
        async def get_info():
            """Get deduplicator plugin information."""
            return {
                "name": "File Deduplicator",
                "version": "0.1.0",
                "type": "utility",
                "capabilities": ["dedup.find_duplicates", "dedup.hash_file"],
                "status": "active" if self.hash_service else "inactive",
                "settings": self.settings.model_dump(),
                "stats": {
                    "files_indexed": len(self._hash_db),
                    "imagehash_available": IMAGEHASH_AVAILABLE
                }
            }
    
    def _find_duplicates(self) -> List[DuplicateGroup]:
        """
        Find all duplicate file groups.
        
        Returns:
            List of duplicate groups
        """
        # Group files by hash value
        hash_groups: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        
        for file_path, hashes in self._hash_db.items():
            for hash_type, hash_value in hashes.items():
                hash_groups[hash_type][hash_value].add(file_path)
        
        # Find groups with more than one file
        duplicate_groups = []
        
        for hash_type, hash_dict in hash_groups.items():
            for hash_value, files in hash_dict.items():
                if len(files) > 1:
                    # Get file size (should be same for all)
                    file_size = self._file_sizes.get(next(iter(files)), 0)
                    
                    duplicate_groups.append(DuplicateGroup(
                        hash=hash_value,
                        hash_type=hash_type,
                        files=sorted(list(files)),
                        file_size=file_size,
                        count=len(files)
                    ))
        
        return duplicate_groups
    
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded.
        Initializes the hash service and registers capabilities.
        """
        logger.info("Loading Deduplicator Plugin...")
        
        # Initialize hash service
        self.hash_service = HashService(self.settings)
        
        # Register capabilities for other plugins
        def find_duplicates() -> List[Dict]:
            """Find all duplicate file groups."""
            groups = self._find_duplicates()
            return [group.model_dump() for group in groups]
        
        def hash_file(file_path: str) -> Dict[str, str]:
            """Calculate hashes for a file."""
            if not self.hash_service:
                return {}
            return self.hash_service.hash_file(file_path)
        
        context.capabilities.register("dedup.find_duplicates", find_duplicates)
        context.capabilities.register("dedup.hash_file", hash_file)
        
        logger.info("Deduplicator Plugin loaded successfully")
        logger.info(f"Hash types enabled: MD5={self.settings.use_md5}, "
                   f"Perceptual={self.settings.use_perceptual_hash}")
        if IMAGEHASH_AVAILABLE:
            logger.info(f"Perceptual hash types: {self.settings.perceptual_hash_types}")
        else:
            logger.warning("imagehash library not available")
    
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        logger.info("Deduplicator Plugin activated")
    
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        logger.info("Deduplicator Plugin deactivated")
