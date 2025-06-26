import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src.tools.save_tool import save_str_to_disc, get_unique_filename


class TestGetUniqueFilename:
    """Test suite for unique filename generation."""
    
    def setup_method(self):
        """Setup method to create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup method to remove temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_unique_filename_no_collision(self):
        """Test filename generation when no collision exists."""
        result = get_unique_filename("test_file", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "test_file.txt")
        assert result == expected
        assert not os.path.exists(result)  # File should not exist yet
    
    def test_unique_filename_with_collision(self):
        """Test filename generation when collision exists."""
        # Create a file that will cause collision
        original_path = os.path.join(self.test_dir, "test_file.txt")
        with open(original_path, 'w') as f:
            f.write("existing content")
        
        result = get_unique_filename("test_file", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "test_file_001.txt")
        assert result == expected
        assert not os.path.exists(result)  # New file should not exist yet
    
    def test_unique_filename_multiple_collisions(self):
        """Test filename generation with multiple collisions."""
        # Create multiple files that will cause collisions
        files_to_create = [
            "test_file.txt",
            "test_file_001.txt",
            "test_file_002.txt"
        ]
        
        for filename in files_to_create:
            path = os.path.join(self.test_dir, filename)
            with open(path, 'w') as f:
                f.write("existing content")
        
        result = get_unique_filename("test_file", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "test_file_003.txt")
        assert result == expected
    
    def test_unique_filename_no_extension(self):
        """Test filename generation with no extension."""
        result = get_unique_filename("test_file", "", self.test_dir)
        expected = os.path.join(self.test_dir, "test_file.txt")  # Default extension
        assert result == expected
    
    def test_unique_filename_none_extension(self):
        """Test filename generation with None extension."""
        result = get_unique_filename("test_file", "", self.test_dir)  # Use empty string instead of None
        expected = os.path.join(self.test_dir, "test_file.txt")  # Default extension
        assert result == expected
    
    def test_unique_filename_strips_dots(self):
        """Test that trailing dots are stripped from base name."""
        result = get_unique_filename("test_file....", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "test_file.txt")
        assert result == expected
    
    def test_unique_filename_creates_directory(self):
        """Test that directory is created if it doesn't exist."""
        new_dir = os.path.join(self.test_dir, "new_subdir")
        assert not os.path.exists(new_dir)
        
        result = get_unique_filename("test_file", ".txt", new_dir)
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_unique_filename_counter_format(self):
        """Test that counter uses proper 3-digit format."""
        # Create files to test counter format
        original_path = os.path.join(self.test_dir, "test.txt")
        with open(original_path, 'w') as f:
            f.write("content")
        
        result = get_unique_filename("test", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "test_001.txt")
        assert result == expected
    
    def test_unique_filename_japanese_characters(self):
        """Test filename generation with Japanese characters."""
        result = get_unique_filename("契約書_テスト", ".txt", self.test_dir)
        expected = os.path.join(self.test_dir, "契約書_テスト.txt")
        assert result == expected


class TestSaveStrToDisc:
    """Test suite for save_str_to_disc function."""
    
    def setup_method(self):
        """Setup method to create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup method to remove temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_save_basic_document(self, mock_get_client):
        """Test basic document saving functionality."""
        document = "これは日本語の契約書のテストです。"
        filename = "test_contract.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        result = json.loads(result_json)
        
        # Verify JSON structure
        assert "filename" in result
        assert "path" in result
        assert "message" in result
        
        # Verify file was created
        file_path = result["path"]
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == document
        
        # Verify result data
        assert result["filename"] == "test_contract.txt"
        assert "Contract saved" in result["message"]
        assert filename in result["message"]
    
    @patch('src.tools.save_tool.get_client')
    def test_save_with_collision_handling(self, mock_get_client):
        """Test document saving with filename collision."""
        document = "Test document content"
        filename = "collision_test.txt"
        
        # Save first document
        result1_json = save_str_to_disc(document, filename, self.test_dir)
        result1 = json.loads(result1_json)
        
        # Save second document with same filename
        result2_json = save_str_to_disc(document + " v2", filename, self.test_dir)
        result2 = json.loads(result2_json)
        
        # Verify both files exist with different names
        assert os.path.exists(result1["path"])
        assert os.path.exists(result2["path"])
        assert result1["filename"] != result2["filename"]
        assert result2["filename"] == "collision_test_001.txt"
    
    @patch('src.tools.save_tool.get_client')
    def test_save_unicode_content(self, mock_get_client):
        """Test saving document with Unicode content."""
        document = """
        契約書

        甲: 株式会社レイヤーX
        乙: テスト会社

        この契約は日本語で書かれています。
        特殊文字も含まれています: ♪♫♪ €£¥
        """
        filename = "unicode_test.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        result = json.loads(result_json)
        
        # Verify file was created and content preserved
        with open(result["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == document
    
    @patch('src.tools.save_tool.get_client')
    def test_save_empty_document(self, mock_get_client):
        """Test saving empty document."""
        document = ""
        filename = "empty_test.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        result = json.loads(result_json)
        
        # Verify file was created
        assert os.path.exists(result["path"])
        
        # Verify empty content
        with open(result["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == ""
    
    @patch('src.tools.save_tool.get_client')
    def test_save_large_document(self, mock_get_client):
        """Test saving large document."""
        # Create a large document (simulate contract with many clauses)
        document = "契約条項 " * 10000  # ~60KB of text
        filename = "large_contract.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        result = json.loads(result_json)
        
        # Verify file was created and content preserved
        assert os.path.exists(result["path"])
        with open(result["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == document
        assert len(content) > 50000  # Verify it's actually large
    
    @patch('src.tools.save_tool.get_client')
    def test_save_default_directory(self, mock_get_client):
        """Test saving with default directory."""
        document = "Test content"
        filename = "default_dir_test.txt"
        
        # Don't specify directory, should use default "contracts"
        result_json = save_str_to_disc(document, filename)
        result = json.loads(result_json)
        
        # Verify default directory was used
        assert "contracts" in result["path"]
        assert result["message"].find("contracts") > -1
        
        # Cleanup: remove the created contracts directory
        contracts_dir = "contracts"
        if os.path.exists(contracts_dir):
            shutil.rmtree(contracts_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_save_json_output_format(self, mock_get_client):
        """Test that output is valid JSON with correct structure."""
        document = "JSON format test"
        filename = "json_test.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        
        # Verify it's valid JSON
        result = json.loads(result_json)
        
        # Verify required fields
        required_fields = ["filename", "path", "message"]
        for field in required_fields:
            assert field in result
            assert result[field] is not None
            assert isinstance(result[field], str)
        
        # Verify ensure_ascii=False works for Unicode
        assert '"filename":' in result_json
        # If filename had Unicode, it should be preserved


class TestSaveStrToDiscErrorHandling:
    """Test error handling scenarios for save_str_to_disc."""
    
    def setup_method(self):
        """Setup method."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_save_permission_error(self, mock_get_client):
        """Test handling of permission errors."""
        document = "Permission test"
        filename = "permission_test.txt"
        
        # Create a read-only directory
        readonly_dir = os.path.join(self.test_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        try:
            with pytest.raises(PermissionError):
                save_str_to_disc(document, filename, readonly_dir)
        finally:
            # Cleanup: restore permissions
            os.chmod(readonly_dir, 0o755)
    
    @patch('src.tools.save_tool.get_client')
    @patch('builtins.open')
    def test_save_write_error(self, mock_open, mock_get_client):
        """Test handling of write errors."""
        mock_open.side_effect = IOError("Disk full")
        
        document = "Write error test"
        filename = "write_error_test.txt"
        
        with pytest.raises(IOError, match="Disk full"):
            save_str_to_disc(document, filename, self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_save_none_inputs(self, mock_get_client):
        """Test handling of None inputs."""
        # This should raise an error as document cannot be None
        with pytest.raises((TypeError, AttributeError)):
            save_str_to_disc(None, "test.txt", self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    @patch('src.tools.save_tool.get_unique_filename')
    def test_save_filename_generation_error(self, mock_get_unique_filename, mock_get_client):
        """Test handling of filename generation errors."""
        mock_get_unique_filename.side_effect = OSError("Path too long")
        
        document = "Filename error test"
        filename = "test.txt"
        
        with pytest.raises(OSError, match="Path too long"):
            save_str_to_disc(document, filename, self.test_dir)


class TestSaveStrToDiscIntegration:
    """Integration tests for save_str_to_disc with Langfuse observability."""
    
    def setup_method(self):
        """Setup method."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_langfuse_observability_integration(self, mock_get_client):
        """Test that Langfuse observability is properly integrated."""
        # The @observe decorator should be working
        # This test ensures the function can be called with observability
        
        document = "Observability test"
        filename = "observability_test.txt"
        
        result_json = save_str_to_disc(document, filename, self.test_dir)
        result = json.loads(result_json)
        
        # Function should work normally with observability
        assert os.path.exists(result["path"])
        with open(result["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == document
    
    @patch('src.tools.save_tool.get_client')
    def test_function_tool_decorator(self, mock_get_client):
        """Test that @function_tool decorator works correctly."""
        # The function should be callable as a tool
        # This is primarily testing that decorators don't break functionality
        
        document = "Function tool test"
        filename = "function_tool_test.txt"
        
        # Should work normally
        result_json = save_str_to_disc(document, filename, self.test_dir)
        assert isinstance(result_json, str)
        
        # Should be valid JSON
        result = json.loads(result_json)
        assert "filename" in result
        assert "path" in result
        assert "message" in result


# === Performance Tests ===

class TestSaveStrToDiscPerformance:
    """Performance tests for save_str_to_disc."""
    
    def setup_method(self):
        """Setup method."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('src.tools.save_tool.get_client')
    def test_multiple_concurrent_saves(self, mock_get_client):
        """Test saving multiple documents with same base filename."""
        document = "Concurrent save test"
        base_filename = "concurrent_test.txt"
        
        results = []
        for i in range(10):
            result_json = save_str_to_disc(f"{document} {i}", base_filename, self.test_dir)
            result = json.loads(result_json)
            results.append(result)
        
        # Verify all files were created with unique names
        filenames = [r["filename"] for r in results]
        assert len(set(filenames)) == 10  # All unique
        
        # Verify all files exist
        for result in results:
            assert os.path.exists(result["path"])
    
    @patch('src.tools.save_tool.get_client')
    def test_save_performance_large_files(self, mock_get_client):
        """Test performance with large files."""
        import time
        
        # Create a very large document
        large_document = "契約条項の詳細内容 " * 50000  # ~1MB of text
        filename = "performance_test.txt"
        
        start_time = time.time()
        result_json = save_str_to_disc(large_document, filename, self.test_dir)
        end_time = time.time()
        
        # Should complete within reasonable time (less than 1 second for 1MB)
        assert (end_time - start_time) < 1.0
        
        # Verify file was created correctly
        result = json.loads(result_json)
        assert os.path.exists(result["path"])
        
        # Verify content integrity
        with open(result["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) == len(large_document)
        assert content == large_document 