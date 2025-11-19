"""Unit tests for ValheimSaveTools wrapper."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import subprocess

from valheim_save_tools_py import ValheimSaveTools
from valheim_save_tools_py.exceptions import (
    JarNotFoundError,
    JavaNotFoundError,
    CommandExecutionError
)


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


class TestInitialization:
    """Test ValheimSaveTools initialization."""
    
    def test_init_with_paths(self, mock_setup):
        """Test initialization with explicit paths."""
        vst = ValheimSaveTools(jar_path="/path/to/tool.jar")
        assert vst.jar_path == Path("/path/to/tool.jar")
        assert vst.java_path == "/usr/bin/java"
        assert vst.verbose is False
        assert vst.fail_on_unsupported_version is False
        assert vst.skip_resolve_names is False
    
    def test_init_with_flags(self, mock_setup):
        """Test initialization with flags."""
        vst = ValheimSaveTools(
            jar_path="/path/to/tool.jar",
            verbose=True,
            fail_on_unsupported_version=True,
            skip_resolve_names=True
        )
        assert vst.verbose is True
        assert vst.fail_on_unsupported_version is True
        assert vst.skip_resolve_names is True
    
    @patch('valheim_save_tools_py.wrapper.Path')
    def test_jar_not_found(self, mock_path, mock_setup):
        """Test initialization fails when JAR not found."""
        # Mock Path to return a non-existent file
        mock_jar = MagicMock()
        mock_jar.exists.return_value = False
        mock_path.return_value = mock_jar
        
        with pytest.raises(JarNotFoundError):
            ValheimSaveTools(jar_path="/nonexistent/tool.jar")
    
    def test_java_not_found(self, mock_setup):
        """Test initialization fails when Java not found."""
        mock_setup['which'].return_value = None
        with pytest.raises(JavaNotFoundError):
            ValheimSaveTools(jar_path="/path/to/tool.jar")


class TestCommonFlags:
    """Test common flags building."""
    
    def test_build_common_flags_none(self, vst):
        """Test no flags when all disabled."""
        flags = vst._build_common_flags()
        assert flags == []
    
    def test_build_common_flags_verbose(self, mock_setup):
        """Test verbose flag."""
        vst = ValheimSaveTools(jar_path="/fake/path.jar", verbose=True)
        flags = vst._build_common_flags()
        assert "-v" in flags
    
    def test_build_common_flags_all(self, mock_setup):
        """Test all flags enabled."""
        vst = ValheimSaveTools(
            jar_path="/fake/path.jar",
            verbose=True,
            fail_on_unsupported_version=True,
            skip_resolve_names=True
        )
        flags = vst._build_common_flags()
        assert "-v" in flags
        assert "--failOnUnsupportedVersion" in flags
        assert "--skipResolveNames" in flags


class TestAutoOutputPath:
    """Test automatic output path generation."""
    
    def test_auto_output_json(self, vst):
        """Test auto-generating JSON output path."""
        output = vst._auto_output_path("world.db", ".json")
        assert output == "world.json"
    
    def test_auto_output_db(self, vst):
        """Test auto-generating DB output path."""
        output = vst._auto_output_path("world.json", ".db")
        assert output == "world.db"
    
    def test_auto_output_with_path(self, vst):
        """Test auto-generating with full path."""
        output = vst._auto_output_path("/path/to/world.db", ".json")
        assert output == "/path/to/world.json"


class TestFileConversion:
    """Test file conversion methods."""
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.tempfile.NamedTemporaryFile')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_auto_output(self, mock_run, mock_remove, mock_exists, mock_temp, mock_open, vst):
        """Test converting to JSON with auto-generated temporary output."""
        # Setup mocks
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/tmpfile.json"
        mock_temp.return_value = mock_tmp
        mock_exists.return_value = True
        
        # Mock JSON data to be returned
        test_data = {"version": 1, "world": "TestWorld"}
        
        # Mock json.load to return test data
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = vst.to_json("world.db")
        
        # Verify it returns parsed JSON data as dict
        assert isinstance(result, dict)
        assert result == test_data
        
        # Verify the command was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        
        # Verify temp file was removed
        mock_remove.assert_called()
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_explicit_output(self, mock_run, mock_open, vst):
        """Test converting to JSON with explicit output file."""
        # Setup mocks
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        # Mock JSON data to be returned
        test_data = {"version": 1, "world": "CustomWorld", "data": [1, 2, 3]}
        
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = vst.to_json("world.db", "custom.json")
        
        # Verify it returns parsed JSON data as dict
        assert isinstance(result, dict)
        assert result == test_data
        
        # Verify the command was called with explicit output
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "custom.json" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_from_json_auto_output(self, mock_run, vst):
        """Test converting from JSON with auto-generated output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.from_json("world.json")
        
        assert result == "world.db"
        args = mock_run.call_args[0][0]
        assert "world.json" in args
        assert "world.db" in args


class TestGlobalKeys:
    """Test global keys operations."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_list_global_keys(self, mock_run, vst):
        """Test listing global keys."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], 
            returncode=0, 
            stdout="defeated_eikthyr\ndefeated_gdking\ndefeated_bonemass\n",
            stderr=""
        )
        
        keys = vst.list_global_keys("world.db")
        
        assert keys == ["defeated_eikthyr", "defeated_gdking", "defeated_bonemass"]
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "--listGlobalKeys" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_add_global_key(self, mock_run, vst):
        """Test adding a global key."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.add_global_key("world.db", "defeated_yagluth")
        
        assert result == "world.db"
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "--addGlobalKey" in args
        assert "defeated_yagluth" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_remove_global_key(self, mock_run, vst):
        """Test removing a global key."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.remove_global_key("world.db", "defeated_eikthyr", "output.db")
        
        assert result == "output.db"
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "output.db" in args
        assert "--removeGlobalKey" in args
        assert "defeated_eikthyr" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_clear_all_global_keys(self, mock_run, vst):
        """Test clearing all global keys."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.clear_all_global_keys("world.db")
        
        args = mock_run.call_args[0][0]
        assert "--removeGlobalKey" in args
        assert "all" in args


class TestStructureProcessing:
    """Test structure processing methods."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_clean_structures_default_threshold(self, mock_run, vst):
        """Test cleaning structures with default threshold."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.clean_structures("world.db")
        
        assert result == "world.db"
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "--cleanStructures" in args
        assert "--cleanStructuresThreshold" in args
        assert "25" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_clean_structures_custom_threshold(self, mock_run, vst):
        """Test cleaning structures with custom threshold."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.clean_structures("world.db", threshold=50)
        
        args = mock_run.call_args[0][0]
        assert "--cleanStructuresThreshold" in args
        assert "50" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_reset_world_simple(self, mock_run, vst):
        """Test resetting world without cleaning."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.reset_world("world.db")
        
        assert result == "world.db"
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "--resetWorld" in args
        mock_run.assert_called_once()
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_reset_world_with_clean(self, mock_run, vst):
        """Test resetting world with cleaning first."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.reset_world("world.db", clean_first=True, clean_threshold=30)
        
        # Should be called twice: once for clean, once for reset
        assert mock_run.call_count == 2
        
        # First call should be clean_structures
        first_call_args = mock_run.call_args_list[0][0][0]
        assert "--cleanStructures" in first_call_args
        assert "--cleanStructuresThreshold" in first_call_args
        assert "30" in first_call_args
        
        # Second call should be reset_world
        second_call_args = mock_run.call_args_list[1][0][0]
        assert "--resetWorld" in second_call_args


class TestFlagsIntegration:
    """Test that flags are properly integrated into commands."""
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_verbose_flag_in_conversion(self, mock_run, mock_open, mock_setup):
        """Test verbose flag is included in conversion."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        test_data = {"version": 1}
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            vst = ValheimSaveTools(jar_path="/fake/path.jar", verbose=True)
            vst.to_json("world.db", "output.json")
        
        args = mock_run.call_args[0][0]
        assert "-v" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_all_flags_in_global_keys(self, mock_run, mock_setup):
        """Test all flags are included in global keys operation."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        vst = ValheimSaveTools(
            jar_path="/fake/path.jar",
            verbose=True,
            fail_on_unsupported_version=True,
            skip_resolve_names=True
        )
        vst.add_global_key("world.db", "test_key")
        
        args = mock_run.call_args[0][0]
        assert "-v" in args
        assert "--failOnUnsupportedVersion" in args
        assert "--skipResolveNames" in args


class TestErrorHandling:
    """Test error handling."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_command_execution_error(self, mock_run, vst):
        """Test command execution error is raised."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Error message"
        )
        
        with pytest.raises(CommandExecutionError) as exc_info:
            vst.to_json("world.db")
        
        assert "Error message" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_timeout_error(self, mock_run, vst):
        """Test timeout error is raised."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        
        with pytest.raises(CommandExecutionError) as exc_info:
            vst.run_command("test", timeout=30)
        
        assert "timed out" in str(exc_info.value).lower()


class TestFileDetection:
    """Test file type detection helpers."""
    
    def test_is_db_file(self):
        """Test .db file detection."""
        assert ValheimSaveTools.is_db_file("world.db") is True
        assert ValheimSaveTools.is_db_file("world.DB") is True
        assert ValheimSaveTools.is_db_file("/path/to/world.db") is True
        assert ValheimSaveTools.is_db_file("world.json") is False
    
    def test_is_fwl_file(self):
        """Test .fwl file detection."""
        assert ValheimSaveTools.is_fwl_file("world.fwl") is True
        assert ValheimSaveTools.is_fwl_file("world.FWL") is True
        assert ValheimSaveTools.is_fwl_file("/path/to/world.fwl") is True
        assert ValheimSaveTools.is_fwl_file("world.db") is False
    
    def test_is_fch_file(self):
        """Test .fch file detection."""
        assert ValheimSaveTools.is_fch_file("character.fch") is True
        assert ValheimSaveTools.is_fch_file("character.FCH") is True
        assert ValheimSaveTools.is_fch_file("/path/to/character.fch") is True
        assert ValheimSaveTools.is_fch_file("character.db") is False
    
    def test_is_json_file(self):
        """Test .json file detection."""
        assert ValheimSaveTools.is_json_file("world.json") is True
        assert ValheimSaveTools.is_json_file("world.JSON") is True
        assert ValheimSaveTools.is_json_file("/path/to/world.json") is True
        assert ValheimSaveTools.is_json_file("world.db") is False
    
    def test_detect_file_type(self):
        """Test file type detection."""
        assert ValheimSaveTools.detect_file_type("world.db") == "db"
        assert ValheimSaveTools.detect_file_type("world.fwl") == "fwl"
        assert ValheimSaveTools.detect_file_type("character.fch") == "fch"
        assert ValheimSaveTools.detect_file_type("world.json") == "json"
        assert ValheimSaveTools.detect_file_type("world.txt") is None
        assert ValheimSaveTools.detect_file_type("/path/to/WORLD.DB") == "db"
    
    def test_is_valheim_file(self):
        """Test generic Valheim file detection."""
        assert ValheimSaveTools.is_valheim_file("world.db") is True
        assert ValheimSaveTools.is_valheim_file("world.fwl") is True
        assert ValheimSaveTools.is_valheim_file("character.fch") is True
        assert ValheimSaveTools.is_valheim_file("world.json") is True
        assert ValheimSaveTools.is_valheim_file("world.txt") is False
        assert ValheimSaveTools.is_valheim_file("readme.md") is False


class TestInputValidation:
    """Test input validation for methods."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_invalid_input(self, mock_run, vst):
        """Test to_json rejects invalid input files."""
        with pytest.raises(ValueError) as exc_info:
            vst.to_json("world.txt")
        
        assert "not a valid Valheim save file" in str(exc_info.value)
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_accepts_db(self, mock_run, mock_open, vst):
        """Test to_json accepts .db files."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        test_data = {"type": "db"}
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = vst.to_json("world.db", "output.json")
        
        mock_run.assert_called_once()
        assert isinstance(result, dict)
        assert result == test_data
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_accepts_fwl(self, mock_run, mock_open, vst):
        """Test to_json accepts .fwl files."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        test_data = {"type": "fwl"}
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = vst.to_json("world.fwl", "output.json")
        
        mock_run.assert_called_once()
        assert isinstance(result, dict)
        assert result == test_data
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_accepts_fch(self, mock_run, mock_open, vst):
        """Test to_json accepts .fch files."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        test_data = {"type": "fch"}
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = vst.to_json("character.fch", "output.json")
        
        mock_run.assert_called_once()
        assert isinstance(result, dict)
        assert result == test_data
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_from_json_invalid_input(self, mock_run, vst):
        """Test from_json rejects non-JSON files."""
        with pytest.raises(ValueError) as exc_info:
            vst.from_json("world.db")
        
        assert "not a JSON file" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_list_global_keys_invalid_input(self, mock_run, vst):
        """Test list_global_keys rejects non-.db files."""
        with pytest.raises(ValueError) as exc_info:
            vst.list_global_keys("world.json")
        
        assert "not a valid .db file" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_add_global_key_invalid_input(self, mock_run, vst):
        """Test add_global_key rejects non-.db files."""
        with pytest.raises(ValueError) as exc_info:
            vst.add_global_key("world.fwl", "key")
        
        assert "not a valid .db file" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_clean_structures_invalid_input(self, mock_run, vst):
        """Test clean_structures rejects non-.db files."""
        with pytest.raises(ValueError) as exc_info:
            vst.clean_structures("world.json")
        
        assert "not a valid .db file" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_reset_world_invalid_input(self, mock_run, vst):
        """Test reset_world rejects non-.db files."""
        with pytest.raises(ValueError) as exc_info:
            vst.reset_world("character.fch")
        
        assert "not a valid .db file" in str(exc_info.value)


class TestSaveFileProcessor:
    """Test SaveFileProcessor builder pattern."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_process_creates_processor(self, mock_run, vst):
        """Test process() creates SaveFileProcessor."""
        from valheim_save_tools_py.wrapper import SaveFileProcessor
        
        processor = vst.process("world.db")
        assert isinstance(processor, SaveFileProcessor)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_process_validates_db_file(self, mock_run, vst):
        """Test process() validates .db file."""
        with pytest.raises(ValueError) as exc_info:
            vst.process("world.json")
        
        assert "not a valid .db file" in str(exc_info.value)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    def test_single_operation_chain(self, mock_remove, mock_exists, mock_copy, mock_run, vst):
        """Test chaining a single operation."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        result = vst.process("world.db").clean_structures().save("output.db")
        
        assert result == "output.db"
        # Verify clean_structures was called
        assert any("--cleanStructures" in str(call) for call in mock_run.call_args_list)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    def test_multiple_operations_chain(self, mock_remove, mock_exists, mock_copy, mock_run, vst):
        """Test chaining multiple operations."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        result = (vst.process("world.db")
                     .clean_structures(threshold=30)
                     .reset_world()
                     .save("output.db"))
        
        assert result == "output.db"
        # Both operations should be called
        assert any("--cleanStructures" in str(call) for call in mock_run.call_args_list)
        assert any("--resetWorld" in str(call) for call in mock_run.call_args_list)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    def test_global_keys_in_chain(self, mock_remove, mock_exists, mock_copy, mock_run, vst):
        """Test chaining global key operations."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        result = (vst.process("world.db")
                     .add_global_key("defeated_eikthyr")
                     .add_global_key("defeated_elder")
                     .save("output.db"))
        
        assert result == "output.db"
        # Both add operations should be called
        add_calls = [call for call in mock_run.call_args_list 
                     if "--addGlobalKey" in str(call)]
        assert len(add_calls) == 2
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    def test_save_without_output_overwrites(self, mock_remove, mock_exists, mock_copy, mock_run, vst):
        """Test save() without output file overwrites original."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        result = vst.process("world.db").clean_structures().save()
        
        assert result == "world.db"
    
    @patch('builtins.open', create=True)
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    def test_to_json_after_operations(self, mock_remove, mock_exists, mock_copy, mock_run, mock_open, vst):
        """Test converting to JSON after operations."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        # Mock JSON data that will be returned
        test_data = {"version": 1, "world": "ProcessedWorld", "cleaned": True}
        
        with patch('valheim_save_tools_py.wrapper.json.load', return_value=test_data):
            result = (vst.process("world.db")
                         .clean_structures()
                         .to_json("output.json"))
        
        # Should return parsed JSON data as dict, not file path
        assert isinstance(result, dict)
        assert result == test_data
        
        # Should have clean_structures and conversion to JSON
        assert any("--cleanStructures" in str(call) for call in mock_run.call_args_list)
        # Last call should be the JSON conversion
        last_call_args = str(mock_run.call_args_list[-1])
        assert "output.json" in last_call_args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    def test_no_operations_save(self, mock_exists, mock_copy, mock_run, vst):
        """Test save() with no operations queued."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        
        result = vst.process("world.db").save("output.db")
        
        assert result == "output.db"
        # Should just copy the file
        mock_copy.assert_called()
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_processor_repr(self, mock_run, vst):
        """Test SaveFileProcessor string representation."""
        processor = vst.process("world.db").clean_structures().reset_world()
        
        repr_str = repr(processor)
        assert "SaveFileProcessor" in repr_str
        assert "world.db" in repr_str
        assert "clean_structures" in repr_str
        assert "reset_world" in repr_str


class TestContextManager:
    """Test context manager functionality."""
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_basic(self, mock_listdir, mock_rmdir, mock_remove, 
                                   mock_exists, mock_copy, mock_run, vst):
        """Test basic context manager usage."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with vst.process("world.db") as processor:
            processor.clean_structures()
        
        # Should execute operations and copy back
        assert mock_run.called
        assert mock_copy.called
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_multiple_operations(self, mock_listdir, mock_rmdir, 
                                                  mock_remove, mock_exists, mock_copy, 
                                                  mock_run, vst):
        """Test context manager with multiple operations."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with vst.process("world.db") as processor:
            processor.clean_structures(threshold=30)
            processor.reset_world()
            processor.add_global_key("defeated_eikthyr")
        
        # All operations should be called
        assert any("--cleanStructures" in str(call) for call in mock_run.call_args_list)
        assert any("--resetWorld" in str(call) for call in mock_run.call_args_list)
        assert any("--addGlobalKey" in str(call) for call in mock_run.call_args_list)
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_chaining(self, mock_listdir, mock_rmdir, mock_remove, 
                                      mock_exists, mock_copy, mock_run, vst):
        """Test context manager with method chaining."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with vst.process("world.db") as processor:
            processor.clean_structures().reset_world().add_global_key("defeated_elder")
        
        # All chained operations should execute
        call_count = len(mock_run.call_args_list)
        assert call_count >= 3
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_no_operations(self, mock_listdir, mock_rmdir, mock_remove, 
                                           mock_exists, mock_copy, mock_run, vst):
        """Test context manager with no operations queued."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with vst.process("world.db") as processor:
            pass  # No operations
        
        # Should still setup and cleanup, but no JAR operations
        # Only the initial copy should happen
        assert mock_copy.called
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_cleanup_on_exception(self, mock_listdir, mock_rmdir, 
                                                   mock_remove, mock_exists, mock_copy, 
                                                   mock_run, vst):
        """Test context manager cleans up even on exception."""
        mock_run.side_effect = Exception("Test error")
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with pytest.raises(Exception) as exc_info:
            with vst.process("world.db") as processor:
                processor.clean_structures()
        
        assert "Test error" in str(exc_info.value)
        # Cleanup should still be called
        assert mock_remove.called or mock_rmdir.called
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    @patch('valheim_save_tools_py.wrapper.shutil.copy2')
    @patch('valheim_save_tools_py.wrapper.os.path.exists')
    @patch('valheim_save_tools_py.wrapper.os.remove')
    @patch('valheim_save_tools_py.wrapper.os.rmdir')
    @patch('valheim_save_tools_py.wrapper.os.listdir')
    def test_context_manager_overwrites_original(self, mock_listdir, mock_rmdir, 
                                                  mock_remove, mock_exists, mock_copy, 
                                                  mock_run, vst):
        """Test context manager overwrites original file."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with vst.process("world.db") as processor:
            processor.clean_structures()
        
        # Should copy the processed file back to the original
        copy_calls = mock_copy.call_args_list
        # At least one call should copy to world.db
        assert any("world.db" in str(call) for call in copy_calls)
