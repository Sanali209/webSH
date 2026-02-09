"""Tests for Deduplicator Plugin."""
import pytest
import os
import tempfile
from pathlib import Path
from plugins.deduplicator.backend import (
    DeduplicatorPlugin,
    HashService,
    DuplicateGroup
)
from plugins.deduplicator.config import DeduplicatorSettings
from core.sdk import PluginContext


class TestHashService:
    """Test the HashService class."""
    
    def test_calculate_md5_consistent(self):
        """Test that MD5 hash is consistent for same content."""
        settings = DeduplicatorSettings()
        service = HashService(settings)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content for MD5 hashing")
            temp_file = f.name
        
        try:
            # Calculate hash twice
            hash1 = service.calculate_md5(temp_file)
            hash2 = service.calculate_md5(temp_file)
            
            assert hash1 is not None
            assert hash2 is not None
            assert hash1 == hash2
            assert len(hash1) == 32  # MD5 is 32 hex characters
        finally:
            os.unlink(temp_file)
    
    def test_calculate_md5_different_content(self):
        """Test that different content produces different MD5 hashes."""
        settings = DeduplicatorSettings()
        service = HashService(settings)
        
        # Create two temporary files with different content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("First file content")
            temp_file1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("Second file content")
            temp_file2 = f2.name
        
        try:
            hash1 = service.calculate_md5(temp_file1)
            hash2 = service.calculate_md5(temp_file2)
            
            assert hash1 is not None
            assert hash2 is not None
            assert hash1 != hash2
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)
    
    def test_calculate_md5_nonexistent_file(self):
        """Test that MD5 calculation returns None for nonexistent file."""
        settings = DeduplicatorSettings()
        service = HashService(settings)
        
        result = service.calculate_md5("/nonexistent/file.txt")
        
        assert result is None
    
    def test_hash_file_md5(self):
        """Test hashing a file with MD5."""
        settings = DeduplicatorSettings(use_md5=True, use_perceptual_hash=False)
        service = HashService(settings)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            hashes = service.hash_file(temp_file, ["md5"])
            
            assert "md5" in hashes
            assert len(hashes["md5"]) == 32
        finally:
            os.unlink(temp_file)
    
    def test_hash_file_too_small(self):
        """Test that files below min size are skipped."""
        settings = DeduplicatorSettings(min_file_size=100)
        service = HashService(settings)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("small")  # Less than 100 bytes
            temp_file = f.name
        
        try:
            hashes = service.hash_file(temp_file)
            
            assert hashes == {}  # Should return empty dict for small files
        finally:
            os.unlink(temp_file)
    
    def test_hash_file_too_large(self):
        """Test that files above max size are skipped."""
        settings = DeduplicatorSettings(max_file_size=10)
        service = HashService(settings)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("This is more than 10 bytes of content")
            temp_file = f.name
        
        try:
            hashes = service.hash_file(temp_file)
            
            assert hashes == {}  # Should return empty dict for large files
        finally:
            os.unlink(temp_file)
    
    def test_is_image(self):
        """Test image file detection."""
        settings = DeduplicatorSettings()
        service = HashService(settings)
        
        assert service.is_image("/path/to/image.jpg") is True
        assert service.is_image("/path/to/image.png") is True
        assert service.is_image("/path/to/file.txt") is False
        assert service.is_image("/path/to/document.pdf") is False


class TestDeduplicatorPlugin:
    """Test the DeduplicatorPlugin class."""
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        plugin = DeduplicatorPlugin()
        
        assert plugin.settings is not None
        assert isinstance(plugin.settings, DeduplicatorSettings)
        assert plugin.router is not None
        assert plugin.hash_service is None  # Not initialized until on_load
    
    def test_plugin_on_load_initializes_service(self):
        """Test that on_load initializes the hash service."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        
        assert plugin.hash_service is None
        
        plugin.on_load(context)
        
        assert plugin.hash_service is not None
        assert isinstance(plugin.hash_service, HashService)
    
    def test_plugin_registers_capabilities(self):
        """Test that the plugin registers its capabilities."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        
        plugin.on_load(context)
        
        # Check that capabilities are registered
        assert context.capabilities.has("dedup.find_duplicates")
        assert context.capabilities.has("dedup.hash_file")
        
        # Verify capabilities are callable
        find_duplicates = context.capabilities.get("dedup.find_duplicates")
        hash_file = context.capabilities.get("dedup.hash_file")
        
        assert callable(find_duplicates)
        assert callable(hash_file)
    
    def test_capability_hash_file(self):
        """Test the hash_file capability."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content for capability")
            temp_file = f.name
        
        try:
            # Get and call the capability
            hash_file = context.capabilities.get("dedup.hash_file")
            result = hash_file(temp_file)
            
            assert isinstance(result, dict)
            assert "md5" in result
        finally:
            os.unlink(temp_file)
    
    def test_capability_find_duplicates(self):
        """Test the find_duplicates capability."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        # Get the capability
        find_duplicates = context.capabilities.get("dedup.find_duplicates")
        result = find_duplicates()
        
        assert isinstance(result, list)
    
    def test_find_duplicates_with_identical_files(self):
        """Test duplicate detection with identical files."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        # Create two identical files
        content = "Identical content for duplication test"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write(content)
            temp_file1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write(content)
            temp_file2 = f2.name
        
        try:
            # Hash both files
            plugin.hash_service.hash_file(temp_file1)
            plugin._hash_db[temp_file1] = plugin.hash_service.hash_file(temp_file1)
            plugin._file_sizes[temp_file1] = os.path.getsize(temp_file1)
            
            plugin._hash_db[temp_file2] = plugin.hash_service.hash_file(temp_file2)
            plugin._file_sizes[temp_file2] = os.path.getsize(temp_file2)
            
            # Find duplicates
            duplicates = plugin._find_duplicates()
            
            # Should find one duplicate group
            assert len(duplicates) > 0
            
            # Check the duplicate group
            md5_group = next((g for g in duplicates if g.hash_type == "md5"), None)
            assert md5_group is not None
            assert md5_group.count == 2
            assert temp_file1 in md5_group.files
            assert temp_file2 in md5_group.files
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)
    
    def test_find_duplicates_no_duplicates(self):
        """Test that no duplicates are found for unique files."""
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        # Create two different files
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("First unique content")
            temp_file1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("Second unique content")
            temp_file2 = f2.name
        
        try:
            # Hash both files
            plugin._hash_db[temp_file1] = plugin.hash_service.hash_file(temp_file1)
            plugin._file_sizes[temp_file1] = os.path.getsize(temp_file1)
            
            plugin._hash_db[temp_file2] = plugin.hash_service.hash_file(temp_file2)
            plugin._file_sizes[temp_file2] = os.path.getsize(temp_file2)
            
            # Find duplicates
            duplicates = plugin._find_duplicates()
            
            # Should find no duplicates
            assert len(duplicates) == 0
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)


@pytest.mark.asyncio
class TestDeduplicatorAPI:
    """Test the API endpoints of the Deduplicator plugin."""
    
    async def test_hash_endpoint(self):
        """Test the /hash endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        # Create test app
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/deduplicator")
        
        client = TestClient(app)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content for API")
            temp_file = f.name
        
        try:
            # Test the hash endpoint
            response = client.post(
                "/api/plugins/deduplicator/hash",
                json={"file_path": temp_file, "hash_types": ["md5"]}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["file_path"] == temp_file
            assert "hashes" in data
            assert "md5" in data["hashes"]
            assert "file_size" in data
        finally:
            os.unlink(temp_file)
    
    async def test_hash_endpoint_nonexistent_file(self):
        """Test the /hash endpoint with nonexistent file."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/deduplicator")
        
        client = TestClient(app)
        
        response = client.post(
            "/api/plugins/deduplicator/hash",
            json={"file_path": "/nonexistent/file.txt"}
        )
        
        assert response.status_code == 404
    
    async def test_duplicates_endpoint(self):
        """Test the /duplicates endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/deduplicator")
        
        client = TestClient(app)
        
        # Create duplicate files
        content = "Duplicate content"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write(content)
            temp_file1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write(content)
            temp_file2 = f2.name
        
        try:
            # Hash the files
            plugin._hash_db[temp_file1] = plugin.hash_service.hash_file(temp_file1)
            plugin._file_sizes[temp_file1] = os.path.getsize(temp_file1)
            plugin._hash_db[temp_file2] = plugin.hash_service.hash_file(temp_file2)
            plugin._file_sizes[temp_file2] = os.path.getsize(temp_file2)
            
            # Test the duplicates endpoint
            response = client.get("/api/plugins/deduplicator/duplicates")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "duplicate_groups" in data
            assert "total_duplicates" in data
            assert "total_groups" in data
            assert "space_wasted" in data
            assert len(data["duplicate_groups"]) > 0
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)
    
    async def test_info_endpoint(self):
        """Test the /info endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = DeduplicatorPlugin()
        context = PluginContext("deduplicator")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/deduplicator")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/deduplicator/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "File Deduplicator"
        assert data["version"] == "0.1.0"
        assert data["type"] == "utility"
        assert data["status"] == "active"
        assert "capabilities" in data
        assert "settings" in data
        assert "stats" in data
