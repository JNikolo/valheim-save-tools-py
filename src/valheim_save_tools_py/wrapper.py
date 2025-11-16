"""Wrapper for Valheim Save Tools JAR."""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Union

from .exceptions import JarNotFoundError, JavaNotFoundError, CommandExecutionError


class ValheimSaveTools:
    """Python wrapper for Valheim Save Tools JAR file."""
    
    def __init__(
        self, 
        jar_path: Optional[str] = None, 
        java_path: Optional[str] = None,
        verbose: bool = False,
        fail_on_unsupported_version: bool = False,
        skip_resolve_names: bool = False
    ):
        self.jar_path = self._find_jar(jar_path)
        self.java_path = self._find_java(java_path)
        self.verbose = verbose
        self.fail_on_unsupported_version = fail_on_unsupported_version
        self.skip_resolve_names = skip_resolve_names
        
    def _find_jar(self, jar_path: Optional[str]) -> Path:
        """Locate the JAR file."""
        if jar_path:
            jar = Path(jar_path)
            if jar.exists():
                return jar
            raise JarNotFoundError(f"JAR not found: {jar_path}")
        
        # Check environment variable
        env_jar = os.getenv("VALHEIM_SAVE_TOOLS_JAR")
        if env_jar:
            jar = Path(env_jar)
            if jar.exists():
                return jar
        
        # Check package directory (bundled JAR)
        package_dir = Path(__file__).parent
        for jar_file in package_dir.glob("*.jar"):
            return jar_file
        
        # Check subdirectories
        for jar_file in package_dir.glob("**/*.jar"):
            return jar_file
        
        raise JarNotFoundError(
            "JAR file not found. Provide jar_path, set VALHEIM_SAVE_TOOLS_JAR, "
            "or place JAR in package directory."
        )
    
    def _find_java(self, java_path: Optional[str]) -> str:
        """Locate Java executable."""
        if java_path:
            if shutil.which(java_path):
                return java_path
            raise JavaNotFoundError(f"Java not found: {java_path}")
        
        java = shutil.which("java")
        if java:
            return java
        
        raise JavaNotFoundError("Java not found in PATH.")
    
    def run_command(
        self,
        *args: str,
        check: bool = True,
        timeout: Optional[int] = None,
        input_data: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Run JAR command."""
        cmd = [self.java_path, "-jar", str(self.jar_path)] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if check and result.returncode != 0:
                raise CommandExecutionError(
                    f"Command failed (exit {result.returncode}): {result.stderr}"
                )
            
            return result
            
        except subprocess.TimeoutExpired:
            raise CommandExecutionError(f"Command timed out after {timeout}s")
        except Exception as e:
            raise CommandExecutionError(f"Command failed: {e}")
    
    def _build_common_flags(self) -> List[str]:
        """Build common flags from instance settings."""
        flags = []
        if self.verbose:
            flags.append("-v")
        if self.fail_on_unsupported_version:
            flags.append("--failOnUnsupportedVersion")
        if self.skip_resolve_names:
            flags.append("--skipResolveNames")
        return flags
    
    def _auto_output_path(self, input_file: str, new_extension: str) -> str:
        """Generate output filename by changing extension."""
        input_path = Path(input_file)
        return str(input_path.with_suffix(new_extension))
    
    # File Conversion Methods
    
    def to_json(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert Valheim save file to JSON.
        
        Args:
            input_file: Path to .db, .fwl, or .fch file
            output_file: Path to output JSON file (auto-generated if None)
            
        Returns:
            Path to the created JSON file
        """
        if (not self.is_db_file(input_file) 
            and not self.is_fwl_file(input_file) 
            and not self.is_fch_file(input_file)):
            raise ValueError(
                f"Input file is not a valid Valheim save file: {input_file} (expected .db, .fwl, or .fch)"
            )
        
        if output_file is None:
            output_file = self._auto_output_path(input_file, ".json")
        
        flags = self._build_common_flags()
        self.run_command(input_file, output_file, *flags)
        return output_file
    
    def from_json(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert JSON back to Valheim save file.
        
        Args:
            input_file: Path to JSON file
            output_file: Path to output save file (auto-generated if None)
            
        Returns:
            Path to the created save file
        """
        if not self.is_json_file(input_file):
            raise ValueError(f"Input file is not a JSON file: {input_file}")
        
        if output_file is None:
            # Try to detect original extension from JSON content or default to .db
            output_file = self._auto_output_path(input_file, ".db")
        
        flags = self._build_common_flags()
        self.run_command(input_file, output_file, *flags)
        return output_file
    
    # Global Keys Operations
    
    def list_global_keys(self, db_file: str) -> List[str]:
        """
        List all global keys in a world database file.
        
        Args:
            db_file: Path to .db file
            
        Returns:
            List of global key names
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        result = self.run_command(db_file, "--listGlobalKeys")
        # Parse output - format is typically one key per line
        keys = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return keys
    
    def add_global_key(self, db_file: str, key: str, output_file: Optional[str] = None) -> str:
        """
        Add a global key to a world database file.
        
        Args:
            db_file: Path to .db file
            key: Global key to add
            output_file: Path to output file (overwrites input if None)
            
        Returns:
            Path to the modified file
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        if output_file is None:
            output_file = db_file
        
        flags = self._build_common_flags()
        self.run_command(db_file, output_file, "--addGlobalKey", key, *flags)
        return output_file
    
    def remove_global_key(self, db_file: str, key: str, output_file: Optional[str] = None) -> str:
        """
        Remove a global key from a world database file.
        
        Args:
            db_file: Path to .db file
            key: Global key to remove (use 'all' to remove all keys)
            output_file: Path to output file (overwrites input if None)
            
        Returns:
            Path to the modified file
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        if output_file is None:
            output_file = db_file
        
        flags = self._build_common_flags()
        self.run_command(db_file, output_file, "--removeGlobalKey", key, *flags)
        return output_file
    
    def clear_all_global_keys(self, db_file: str, output_file: Optional[str] = None) -> str:
        """
        Remove all global keys from a world database file.
        
        Args:
            db_file: Path to .db file
            output_file: Path to output file (overwrites input if None)
            
        Returns:
            Path to the modified file
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        return self.remove_global_key(db_file, "all", output_file)
    
    # Structure Processing Methods
    
    def clean_structures(
        self, 
        db_file: str, 
        output_file: Optional[str] = None,
        threshold: int = 25
    ) -> str:
        """
        Clean up player-built structures smaller than threshold.
        
        Args:
            db_file: Path to .db file
            output_file: Path to output file (overwrites input if None)
            threshold: Minimum structures to consider as a base (default 25)
            
        Returns:
            Path to the modified file
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        if output_file is None:
            output_file = db_file
        
        flags = self._build_common_flags()
        self.run_command(
            db_file, 
            output_file, 
            "--cleanStructures",
            "--cleanStructuresThreshold", str(threshold),
            *flags
        )
        return output_file
    
    def reset_world(
        self, 
        db_file: str, 
        output_file: Optional[str] = None,
        clean_first: bool = False,
        clean_threshold: int = 25
    ) -> str:
        """
        Reset world zones without player structures.
        
        Args:
            db_file: Path to .db file
            output_file: Path to output file (overwrites input if None)
            clean_first: Run clean_structures before reset (recommended)
            clean_threshold: Threshold for clean_structures if clean_first=True
            
        Returns:
            Path to the modified file
        """
        if not self.is_db_file(db_file):
            raise ValueError(f"Input file is not a valid .db file: {db_file}")
        
        if output_file is None:
            output_file = db_file
        
        # If clean_first, run clean_structures as preprocessor
        if clean_first:
            db_file = self.clean_structures(db_file, db_file, clean_threshold)
        
        flags = self._build_common_flags()
        self.run_command(db_file, output_file, "--resetWorld", *flags)
        return output_file
    
    # File Type Detection Helpers
    
    @staticmethod
    def is_db_file(file_path: str) -> bool:
        """
        Check if file is a Valheim world database file (.db).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has .db extension
        """
        return Path(file_path).suffix.lower() == ".db"
    
    @staticmethod
    def is_fwl_file(file_path: str) -> bool:
        """
        Check if file is a Valheim world metadata file (.fwl).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has .fwl extension
        """
        return Path(file_path).suffix.lower() == ".fwl"
    
    @staticmethod
    def is_fch_file(file_path: str) -> bool:
        """
        Check if file is a Valheim character file (.fch).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has .fch extension
        """
        return Path(file_path).suffix.lower() == ".fch"
    
    @staticmethod
    def is_json_file(file_path: str) -> bool:
        """
        Check if file is a JSON file (.json).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has .json extension
        """
        return Path(file_path).suffix.lower() == ".json"
    
    @staticmethod
    def detect_file_type(file_path: str) -> Optional[str]:
        """
        Detect Valheim save file type from extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type: 'db', 'fwl', 'fch', 'json', or None if unknown
        """
        suffix = Path(file_path).suffix.lower()
        type_map = {
            ".db": "db",
            ".fwl": "fwl",
            ".fch": "fch",
            ".json": "json"
        }
        return type_map.get(suffix)
    
    @staticmethod
    def is_valheim_file(file_path: str) -> bool:
        """
        Check if file is any Valheim save file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is .db, .fwl, .fch, or .json
        """
        return ValheimSaveTools.detect_file_type(file_path) is not None
