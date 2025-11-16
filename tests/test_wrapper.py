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
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_auto_output(self, mock_run, vst):
        """Test converting to JSON with auto-generated output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.to_json("world.db")
        
        assert result == "world.json"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "world.db" in args
        assert "world.json" in args
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_to_json_explicit_output(self, mock_run, vst):
        """Test converting to JSON with explicit output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        result = vst.to_json("world.db", "custom.json")
        
        assert result == "custom.json"
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
    
    @patch('valheim_save_tools_py.wrapper.subprocess.run')
    def test_verbose_flag_in_conversion(self, mock_run, mock_setup):
        """Test verbose flag is included in conversion."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        
        vst = ValheimSaveTools(jar_path="/fake/path.jar", verbose=True)
        vst.to_json("world.db")
        
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
