"""Unit tests for file-like object support in ValheimSaveTools wrapper."""

import pytest
from pathlib import Path
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json

from valheim_save_tools_py import ValheimSaveTools


@pytest.fixture
def mock_setup():
    """Setup common mocks for tests."""
    with patch('valheim_save_tools_py.wrapper.shutil.which') as mock_which, \
         patch('valheim_save_tools_py.wrapper.Path.exists') as mock_exists, \
         patch('valheim_save_tools_py.wrapper.Path.glob') as mock_glob:
        
        mock_exists.return_value = True
        mock_which.return_value = "/usr/bin/java"
        mock_glob.return_value = []
        
        yield {
            'which': mock_which,
            'exists': mock_exists,
            'glob': mock_glob
        }


@pytest.fixture
def vst(mock_setup):
    """Create ValheimSaveTools instance with mocks."""
    return ValheimSaveTools(jar_path="/fake/path.jar")


class TestFilelikeDetection:
    """Test file-like object detection."""
    
    def test_is_file_like_with_bytesio(self):
        """Test detection of BytesIO as file-like."""
        bio = BytesIO(b"test data")
        assert ValheimSaveTools._is_file_like(bio) is True
    
    def test_is_file_like_with_string(self):
        """Test string is not detected as file-like."""
        assert ValheimSaveTools._is_file_like("/path/to/file.db") is False
    
    def test_is_file_like_with_path(self):
        """Test Path object is not detected as file-like."""
        assert ValheimSaveTools._is_file_like(Path("/path/to/file.db")) is False
    
    def test_is_file_like_with_file_object(self):
        """Test file object is detected as file-like."""
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            assert ValheimSaveTools._is_file_like(f) is True


class TestResolveInput:
    """Test input resolution."""
    
    def test_resolve_input_with_path(self, vst):
        """Test resolving file path."""
        path, is_temp = vst._resolve_input("/path/to/file.db")
        assert path == "/path/to/file.db"
        assert is_temp is False
    
    def test_resolve_input_with_bytesio(self, vst):
        """Test resolving BytesIO object."""
        bio = BytesIO(b"test data")
        path, is_temp = vst._resolve_input(bio, suffix=".db")
        
        assert path.endswith(".db")
        assert is_temp is True
        
        # Verify temp file was created with correct content
        with open(path, 'rb') as f:
            assert f.read() == b"test data"
        
        # Cleanup
        import os
        if os.path.exists(path):
            os.remove(path)


class TestToJsonWithFilelike:
    """Test to_json with file-like objects."""
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_to_json_bytesio_input(self, mock_run, vst):
        """Test to_json with BytesIO input."""
        # Create fake .db content
        db_content = b"fake db content"
        bio = BytesIO(db_content)
        
        # Mock the run_command to create a JSON file
        def create_json_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'w') as f:
                json.dump({"test": "data"}, f)
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_json_output
        
        # Run to_json
        result = vst.to_json(bio)
        
        # Verify result
        assert result == {"test": "data"}
        assert mock_run.called
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_to_json_bytesio_output(self, mock_run, vst, tmp_path):
        """Test to_json with BytesIO output."""
        # Create a test input file
        input_file = tmp_path / "test.db"
        input_file.write_bytes(b"fake db content")
        
        # Mock the run_command to create a JSON file
        def create_json_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'w') as f:
                json.dump({"test": "data"}, f)
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_json_output
        
        # Run to_json with BytesIO output
        output_bio = BytesIO()
        result = vst.to_json(str(input_file), output_bio)
        
        # Verify result
        assert result == {"test": "data"}
        
        # Verify output was written to BytesIO
        output_bio.seek(0)
        output_data = output_bio.read()
        assert len(output_data) > 0


class TestFromJsonWithFilelike:
    """Test from_json with file-like objects."""
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_from_json_bytesio_input(self, mock_run, vst):
        """Test from_json with BytesIO input."""
        # Create fake JSON content
        json_content = json.dumps({"test": "data"}).encode('utf-8')
        bio = BytesIO(json_content)
        
        # Mock the run_command to create a .db file
        def create_db_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"fake db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_db_output
        
        # Run from_json
        result = vst.from_json(bio)
        
        # Verify result is a file path
        assert result is not None
        assert result.endswith(".db")
        assert mock_run.called
        
        # Cleanup
        import os
        if result and os.path.exists(result):
            os.remove(result)
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_from_json_bytesio_output(self, mock_run, vst, tmp_path):
        """Test from_json with BytesIO output."""
        # Create a test input file
        input_file = tmp_path / "test.json"
        input_file.write_text(json.dumps({"test": "data"}))
        
        # Mock the run_command to create a .db file
        def create_db_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"fake db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_db_output
        
        # Run from_json with BytesIO output
        output_bio = BytesIO()
        result = vst.from_json(str(input_file), output_bio)
        
        # Verify result is None (because output was file-like)
        assert result is None
        
        # Verify output was written to BytesIO
        output_bio.seek(0)
        output_data = output_bio.read()
        assert output_data == b"fake db content"


class TestGlobalKeysWithFilelike:
    """Test global key operations with file-like objects."""
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_list_global_keys_bytesio(self, mock_run, vst):
        """Test list_global_keys with BytesIO input."""
        # Create fake .db content
        db_content = b"fake db content"
        bio = BytesIO(db_content)
        
        # Mock the run_command output
        mock_result = MagicMock()
        mock_result.stdout = "defeated_eikthyr\ndefeated_gdking\n"
        mock_run.return_value = mock_result
        
        # Run list_global_keys
        keys = vst.list_global_keys(bio)
        
        # Verify result
        assert keys == ["defeated_eikthyr", "defeated_gdking"]
        assert mock_run.called
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_add_global_key_bytesio_inplace(self, mock_run, vst):
        """Test add_global_key with BytesIO input (in-place modification)."""
        # Create fake .db content
        db_content = b"fake db content"
        bio = BytesIO(db_content)
        
        # Mock the run_command to create modified output
        def create_modified_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"modified db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_modified_output
        
        # Run add_global_key without explicit output
        result = vst.add_global_key(bio, "defeated_eikthyr")
        
        # Verify result is None (in-place modification)
        assert result is None
        
        # Verify BytesIO was updated
        bio.seek(0)
        assert bio.read() == b"modified db content"
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_add_global_key_bytesio_output(self, mock_run, vst, tmp_path):
        """Test add_global_key with BytesIO output."""
        # Create a test input file
        input_file = tmp_path / "test.db"
        input_file.write_bytes(b"fake db content")
        
        # Mock the run_command to create modified output
        def create_modified_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"modified db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_modified_output
        
        # Run add_global_key with BytesIO output
        output_bio = BytesIO()
        result = vst.add_global_key(str(input_file), "defeated_eikthyr", output_bio)
        
        # Verify result is None
        assert result is None
        
        # Verify output was written to BytesIO
        output_bio.seek(0)
        assert output_bio.read() == b"modified db content"


class TestStructureOperationsWithFilelike:
    """Test structure operations with file-like objects."""
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_clean_structures_bytesio(self, mock_run, vst):
        """Test clean_structures with BytesIO."""
        # Create fake .db content
        db_content = b"fake db content"
        bio = BytesIO(db_content)
        
        # Mock the run_command to create modified output
        def create_modified_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"cleaned db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_modified_output
        
        # Run clean_structures
        result = vst.clean_structures(bio, threshold=30)
        
        # Verify result is None (in-place modification)
        assert result is None
        
        # Verify BytesIO was updated
        bio.seek(0)
        assert bio.read() == b"cleaned db content"
    
    @patch('valheim_save_tools_py.wrapper.ValheimSaveTools.run_command')
    def test_reset_world_bytesio_output(self, mock_run, vst, tmp_path):
        """Test reset_world with BytesIO output."""
        # Create a test input file
        input_file = tmp_path / "test.db"
        input_file.write_bytes(b"fake db content")
        
        # Mock the run_command to create modified output
        def create_modified_output(*args, **kwargs):
            output_path = args[1]
            with open(output_path, 'wb') as f:
                f.write(b"reset db content")
            return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = create_modified_output
        
        # Run reset_world with BytesIO output
        output_bio = BytesIO()
        result = vst.reset_world(str(input_file), output_bio)
        
        # Verify result is None
        assert result is None
        
        # Verify output was written to BytesIO
        output_bio.seek(0)
        assert output_bio.read() == b"reset db content"
