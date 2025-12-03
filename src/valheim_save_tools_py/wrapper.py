"""Wrapper for Valheim Save Tools JAR."""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Union, BinaryIO
import json
import io

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
    
    @staticmethod
    def _is_file_like(obj) -> bool:
        """
        Check if object is file-like (has read method).
        
        Args:
            obj: Object to check
            
        Returns:
            True if object has read method
        """
        return hasattr(obj, 'read') and callable(getattr(obj, 'read'))
    
    def _resolve_input(self, input_source: Union[str, BinaryIO], suffix: str = "") -> tuple[str, bool]:
        """
        Resolve input to a file path, creating temp file if needed.
        
        Args:
            input_source: File path or file-like object
            suffix: File suffix for temp file (e.g., '.db', '.json')
            
        Returns:
            Tuple of (file_path, is_temp_file)
        """
        if self._is_file_like(input_source):
            # Create temp file and write content
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            try:
                # Save current position if seekable
                original_position = None
                if hasattr(input_source, 'seek') and hasattr(input_source, 'tell'):
                    try:
                        original_position = input_source.tell()
                    except (OSError, IOError):
                        pass
                
                # Ensure we're reading in binary mode
                if hasattr(input_source, 'mode') and 'b' not in input_source.mode:
                    # Text mode file-like object
                    content = input_source.read()
                    if isinstance(content, str):
                        tmp.write(content.encode('utf-8'))
                    else:
                        tmp.write(content)
                else:
                    # Binary mode or BytesIO
                    content = input_source.read()
                    tmp.write(content)
                
                # Reset file pointer to original position for reuse
                if original_position is not None:
                    try:
                        input_source.seek(original_position)
                    except (OSError, IOError):
                        pass
                
                tmp.close()
                return tmp.name, True
            except Exception as e:
                tmp.close()
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
                raise ValueError(f"Failed to read from file-like object: {e}")
        else:
            # Assume it's a file path
            return str(input_source), False
    
    def _write_output(self, file_path: str, output_dest: Union[str, BinaryIO, None]) -> Optional[str]:
        """
        Write file content to output destination.
        
        Args:
            file_path: Path to source file
            output_dest: Destination (file path, file-like object, or None)
            
        Returns:
            Output file path if output_dest was a path, None otherwise
        """
        if output_dest is None:
            return None
        
        if self._is_file_like(output_dest):
            # Write to file-like object
            with open(file_path, 'rb') as f:
                output_dest.write(f.read())
            return None
        else:
            # It's a file path, copy the file
            if file_path != str(output_dest):
                shutil.copy2(file_path, str(output_dest))
            return str(output_dest)

    
    # File Conversion Methods
    
    def to_json(
        self, 
        input_file: Union[str, BinaryIO], 
        output_file: Union[str, BinaryIO, None] = None,
        input_file_type: Optional[str] = None
    ) -> Dict:
        """
        Convert Valheim save file to JSON.
        
        Args:
            input_file: Path to .db, .fwl, or .fch file, or file-like object
            output_file: Path to output JSON file, file-like object, or None
            input_file_type: For file-like objects, hint the file type ('db', 'fwl', or 'fch').
                           If not provided, defaults to 'db'. Ignored for file paths.
            
        Returns:
            Parsed JSON data as dictionary. If output_file is provided, also saves to that file.
        """
        # Determine suffix for temp file
        if self._is_file_like(input_file):
            # Use provided hint or default to .db
            if input_file_type:
                suffix = f".{input_file_type.lstrip('.')}"
            else:
                suffix = ".db"
        else:
            # For file paths, preserve the original extension
            suffix = Path(str(input_file)).suffix or ".db"
        
        # Resolve input to file path
        input_path, input_is_temp = self._resolve_input(input_file, suffix=suffix)
        
        try:
            # Check file type based on path if available
            if not self._is_file_like(input_file):
                if (not self.is_db_file(input_path) 
                    and not self.is_fwl_file(input_path) 
                    and not self.is_fch_file(input_path)):
                    raise ValueError(
                        f"Input file is not a valid Valheim save file: {input_path} (expected .db, .fwl, or .fch)"
                    )
            
            # Determine output path
            tmp_output = None
            if output_file is None or self._is_file_like(output_file):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
                tmp_output = tmp.name
                tmp.close()
                output_path = tmp_output
            else:
                output_path = str(output_file)
            
            # Run conversion
            flags = self._build_common_flags()
            self.run_command(input_path, output_path, *flags)
            
            # Read JSON data
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle output
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            
            # Cleanup temp files
            if tmp_output and os.path.exists(tmp_output):
                os.remove(tmp_output)
            
            return data
            
        finally:
            # Cleanup temp input file if created
            if input_is_temp and os.path.exists(input_path):
                os.remove(input_path)
    
    def from_json(
        self, 
        input_file: Union[str, BinaryIO], 
        output_file: Union[str, BinaryIO, None] = None
    ) -> Union[str, None]:
        """
        Convert JSON back to Valheim save file.
        
        Args:
            input_file: Path to JSON file or file-like object
            output_file: Path to output save file, file-like object, or None (auto-generated if None)
            
        Returns:
            Path to the created save file (if output_file is a path), or None (if output_file is file-like)
        """
        # Resolve input to file path
        input_path, input_is_temp = self._resolve_input(input_file, suffix=".json")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(input_file) and not self.is_json_file(input_path):
                raise ValueError(f"Input file is not a JSON file: {input_path}")
            
            # Determine output path
            output_is_temp = False
            if output_file is None:
                # Auto-generate output path
                output_path = self._auto_output_path(input_path, ".db")
            elif self._is_file_like(output_file):
                # Create temp file for file-like output
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                output_path = tmp.name
                tmp.close()
                output_is_temp = True
            else:
                output_path = str(output_file)
            
            # Run conversion
            flags = self._build_common_flags()
            self.run_command(input_path, output_path, *flags)
            
            # Handle output
            result = None
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            else:
                result = output_path
            
            # Cleanup temp output file if created
            if output_is_temp and os.path.exists(output_path):
                os.remove(output_path)
            
            return result
            
        finally:
            # Cleanup temp input file if created
            if input_is_temp and os.path.exists(input_path):
                os.remove(input_path)
    
    # Global Keys Operations
    
    def list_global_keys(self, db_file: Union[str, BinaryIO]) -> List[str]:
        """
        List all global keys in a world database file.
        
        Args:
            db_file: Path to .db file or file-like object
            
        Returns:
            List of global key names
        """
        # Resolve input to file path
        db_path, db_is_temp = self._resolve_input(db_file, suffix=".db")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(db_file) and not self.is_db_file(db_path):
                raise ValueError(f"Input file is not a valid .db file: {db_path}")
            
            result = self.run_command(db_path, "--listGlobalKeys")
            # Parse output - format is typically one key per line
            keys = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            return keys
            
        finally:
            # Cleanup temp file if created
            if db_is_temp and os.path.exists(db_path):
                os.remove(db_path)
    
    def add_global_key(
        self, 
        db_file: Union[str, BinaryIO], 
        key: str, 
        output_file: Union[str, BinaryIO, None] = None
    ) -> Optional[str]:
        """
        Add a global key to a world database file.
        
        Args:
            db_file: Path to .db file or file-like object
            key: Global key to add
            output_file: Path to output file, file-like object, or None (overwrites input if None and input is path)
            
        Returns:
            Path to the modified file (if output is a path), or None (if output is file-like or input was file-like)
        """
        # Resolve input to file path
        db_path, db_is_temp = self._resolve_input(db_file, suffix=".db")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(db_file) and not self.is_db_file(db_path):
                raise ValueError(f"Input file is not a valid .db file: {db_path}")
            
            # Determine output path
            output_is_temp = False
            if output_file is None:
                if self._is_file_like(db_file):
                    # For file-like input without output, create temp file
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                    output_path = tmp.name
                    tmp.close()
                    output_is_temp = True
                else:
                    # For path input without output, overwrite input
                    output_path = db_path
            elif self._is_file_like(output_file):
                # Create temp file for file-like output
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                output_path = tmp.name
                tmp.close()
                output_is_temp = True
            else:
                output_path = str(output_file)
            
            # Run command
            flags = self._build_common_flags()
            self.run_command(db_path, output_path, "--addGlobalKey", key, *flags)
            
            # Handle output
            result = None
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            elif self._is_file_like(db_file) and output_file is None:
                # Write back to file-like input
                with open(output_path, 'rb') as f:
                    db_file.seek(0)
                    db_file.write(f.read())
                    db_file.truncate()
            else:
                result = output_path
            
            # Cleanup temp output file if created
            if output_is_temp and os.path.exists(output_path):
                os.remove(output_path)
            
            return result
            
        finally:
            # Cleanup temp input file if created
            if db_is_temp and os.path.exists(db_path):
                os.remove(db_path)
    
    def remove_global_key(
        self, 
        db_file: Union[str, BinaryIO], 
        key: str, 
        output_file: Union[str, BinaryIO, None] = None
    ) -> Optional[str]:
        """
        Remove a global key from a world database file.
        
        Args:
            db_file: Path to .db file or file-like object
            key: Global key to remove (use 'all' to remove all keys)
            output_file: Path to output file, file-like object, or None (overwrites input if None and input is path)
            
        Returns:
            Path to the modified file (if output is a path), or None (if output is file-like or input was file-like)
        """
        # Resolve input to file path
        db_path, db_is_temp = self._resolve_input(db_file, suffix=".db")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(db_file) and not self.is_db_file(db_path):
                raise ValueError(f"Input file is not a valid .db file: {db_path}")
            
            # Determine output path
            output_is_temp = False
            if output_file is None:
                if self._is_file_like(db_file):
                    # For file-like input without output, create temp file
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                    output_path = tmp.name
                    tmp.close()
                    output_is_temp = True
                else:
                    # For path input without output, overwrite input
                    output_path = db_path
            elif self._is_file_like(output_file):
                # Create temp file for file-like output
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                output_path = tmp.name
                tmp.close()
                output_is_temp = True
            else:
                output_path = str(output_file)
            
            # Run command
            flags = self._build_common_flags()
            self.run_command(db_path, output_path, "--removeGlobalKey", key, *flags)
            
            # Handle output
            result = None
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            elif self._is_file_like(db_file) and output_file is None:
                # Write back to file-like input
                with open(output_path, 'rb') as f:
                    db_file.seek(0)
                    db_file.write(f.read())
                    db_file.truncate()
            else:
                result = output_path
            
            # Cleanup temp output file if created
            if output_is_temp and os.path.exists(output_path):
                os.remove(output_path)
            
            return result
            
        finally:
            # Cleanup temp input file if created
            if db_is_temp and os.path.exists(db_path):
                os.remove(db_path)
    
    def clear_all_global_keys(
        self, 
        db_file: Union[str, BinaryIO], 
        output_file: Union[str, BinaryIO, None] = None
    ) -> Optional[str]:
        """
        Remove all global keys from a world database file.
        
        Args:
            db_file: Path to .db file or file-like object
            output_file: Path to output file, file-like object, or None (overwrites input if None and input is path)
            
        Returns:
            Path to the modified file (if output is a path), or None (if output is file-like or input was file-like)
        """
        return self.remove_global_key(db_file, "all", output_file)
    
    # Structure Processing Methods
    
    def clean_structures(
        self, 
        db_file: Union[str, BinaryIO], 
        output_file: Union[str, BinaryIO, None] = None,
        threshold: int = 25
    ) -> Optional[str]:
        """
        Clean up player-built structures smaller than threshold.
        
        Args:
            db_file: Path to .db file or file-like object
            output_file: Path to output file, file-like object, or None (overwrites input if None and input is path)
            threshold: Minimum structures to consider as a base (default 25)
            
        Returns:
            Path to the modified file (if output is a path), or None (if output is file-like or input was file-like)
        """
        # Resolve input to file path
        db_path, db_is_temp = self._resolve_input(db_file, suffix=".db")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(db_file) and not self.is_db_file(db_path):
                raise ValueError(f"Input file is not a valid .db file: {db_path}")
            
            # Determine output path
            output_is_temp = False
            if output_file is None:
                if self._is_file_like(db_file):
                    # For file-like input without output, create temp file
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                    output_path = tmp.name
                    tmp.close()
                    output_is_temp = True
                else:
                    # For path input without output, overwrite input
                    output_path = db_path
            elif self._is_file_like(output_file):
                # Create temp file for file-like output
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                output_path = tmp.name
                tmp.close()
                output_is_temp = True
            else:
                output_path = str(output_file)
            
            # Run command
            flags = self._build_common_flags()
            self.run_command(
                db_path, 
                output_path, 
                "--cleanStructures",
                "--cleanStructuresThreshold", str(threshold),
                *flags
            )
            
            # Handle output
            result = None
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            elif self._is_file_like(db_file) and output_file is None:
                # Write back to file-like input
                with open(output_path, 'rb') as f:
                    db_file.seek(0)
                    db_file.write(f.read())
                    db_file.truncate()
            else:
                result = output_path
            
            # Cleanup temp output file if created
            if output_is_temp and os.path.exists(output_path):
                os.remove(output_path)
            
            return result
            
        finally:
            # Cleanup temp input file if created
            if db_is_temp and os.path.exists(db_path):
                os.remove(db_path)
    
    def reset_world(
        self, 
        db_file: Union[str, BinaryIO], 
        output_file: Union[str, BinaryIO, None] = None,
        clean_first: bool = False,
        clean_threshold: int = 25
    ) -> Optional[str]:
        """
        Reset world zones without player structures.
        
        Args:
            db_file: Path to .db file or file-like object
            output_file: Path to output file, file-like object, or None (overwrites input if None and input is path)
            clean_first: Run clean_structures before reset (recommended)
            clean_threshold: Threshold for clean_structures if clean_first=True
            
        Returns:
            Path to the modified file (if output is a path), or None (if output is file-like or input was file-like)
        """
        # Resolve input to file path
        db_path, db_is_temp = self._resolve_input(db_file, suffix=".db")
        
        try:
            # Check file type if path was provided
            if not self._is_file_like(db_file) and not self.is_db_file(db_path):
                raise ValueError(f"Input file is not a valid .db file: {db_path}")
            
            # If clean_first, run clean_structures as preprocessor
            if clean_first:
                db_path = self.clean_structures(db_path, db_path, clean_threshold)
            
            # Determine output path
            output_is_temp = False
            if output_file is None:
                if self._is_file_like(db_file):
                    # For file-like input without output, create temp file
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                    output_path = tmp.name
                    tmp.close()
                    output_is_temp = True
                else:
                    # For path input without output, overwrite input
                    output_path = db_path
            elif self._is_file_like(output_file):
                # Create temp file for file-like output
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                output_path = tmp.name
                tmp.close()
                output_is_temp = True
            else:
                output_path = str(output_file)
            
            # Run command
            flags = self._build_common_flags()
            self.run_command(db_path, output_path, "--resetWorld", *flags)
            
            # Handle output
            result = None
            if output_file is not None and self._is_file_like(output_file):
                # Write to file-like object
                with open(output_path, 'rb') as f:
                    output_file.write(f.read())
            elif self._is_file_like(db_file) and output_file is None:
                # Write back to file-like input
                with open(output_path, 'rb') as f:
                    db_file.seek(0)
                    db_file.write(f.read())
                    db_file.truncate()
            else:
                result = output_path
            
            # Cleanup temp output file if created
            if output_is_temp and os.path.exists(output_path):
                os.remove(output_path)
            
            return result
            
        finally:
            # Cleanup temp input file if created
            if db_is_temp and os.path.exists(db_path):
                os.remove(db_path)
    
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
    
    def process(self, input_file: str) -> 'SaveFileProcessor':
        """
        Create a processor for chaining operations.
        
        Args:
            input_file: Path to the file to process
            
        Returns:
            SaveFileProcessor instance for chaining operations
            
        Example:
            >>> vst = ValheimSaveTools()
            >>> vst.process("world.db") \\
            ...    .clean_structures(threshold=30) \\
            ...    .reset_world() \\
            ...    .save("cleaned_world.db")
        """
        return SaveFileProcessor(self, input_file)


class SaveFileProcessor:
    """
    Fluent interface for chaining operations on Valheim save files.
    
    This class provides a builder pattern for performing multiple operations
    on a save file in sequence. Operations are performed on a working copy
    and can be saved to a new file or overwrite the original.
    
    Example:
        >>> vst = ValheimSaveTools()
        >>> processor = vst.process("world.db")
        >>> processor.clean_structures().reset_world().save("clean_world.db")
    """
    
    def __init__(self, tools: ValheimSaveTools, input_file: str):
        """
        Initialize processor.
        
        Args:
            tools: ValheimSaveTools instance
            input_file: Path to input file
        """
        if not ValheimSaveTools.is_db_file(input_file):
            raise ValueError(f"{input_file} is not a valid .db file")
        
        self._tools = tools
        self._input_file = input_file
        self._current_file = input_file
        self._operations = []
        self._temp_files = []
        self._temp_dir = None
        self._in_context = False
    
    def clean_structures(self, threshold: int = 25) -> 'SaveFileProcessor':
        """
        Queue structure cleaning operation.
        
        Args:
            threshold: Distance threshold for structure removal (default: 25)
            
        Returns:
            Self for chaining
        """
        self._operations.append(('clean_structures', {'threshold': threshold}))
        return self
    
    def reset_world(self) -> 'SaveFileProcessor':
        """
        Queue world reset operation.
        
        Returns:
            Self for chaining
        """
        self._operations.append(('reset_world', {}))
        return self
    
    def add_global_key(self, key: str) -> 'SaveFileProcessor':
        """
        Queue global key addition.
        
        Args:
            key: Global key to add
            
        Returns:
            Self for chaining
        """
        self._operations.append(('add_global_key', {'key': key}))
        return self
    
    def remove_global_key(self, key: str) -> 'SaveFileProcessor':
        """
        Queue global key removal.
        
        Args:
            key: Global key to remove
            
        Returns:
            Self for chaining
        """
        self._operations.append(('remove_global_key', {'key': key}))
        return self
    
    def clear_all_global_keys(self) -> 'SaveFileProcessor':
        """
        Queue clearing all global keys.
        
        Returns:
            Self for chaining
        """
        self._operations.append(('clear_all_global_keys', {}))
        return self
    
    def _execute_operations(self) -> str:
        """
        Execute all queued operations.
        
        Returns:
            Path to the final processed file
        """
        if not self._operations:
            # No operations, just return input file
            return self._current_file
        
        # Create temp directory for intermediate files
        temp_dir = tempfile.mkdtemp(prefix="valheim_processor_")
        self._temp_dir = temp_dir
        
        # Copy input file to temp directory as working copy
        working_file = os.path.join(temp_dir, os.path.basename(self._input_file))
        shutil.copy2(self._current_file, working_file)
        self._temp_files.append(working_file)
        
        # Execute each operation in sequence
        for operation, kwargs in self._operations:
            if operation == 'clean_structures':
                self._tools.clean_structures(working_file, **kwargs)
            elif operation == 'reset_world':
                self._tools.reset_world(working_file)
            elif operation == 'add_global_key':
                self._tools.add_global_key(working_file, **kwargs)
            elif operation == 'remove_global_key':
                self._tools.remove_global_key(working_file, **kwargs)
            elif operation == 'clear_all_global_keys':
                self._tools.clear_all_global_keys(working_file)
        
        return working_file
    
    def save(self, output_file: Optional[str] = None) -> str:
        """
        Execute all operations and save the result.
        
        Args:
            output_file: Path to save result (default: overwrite input file)
            
        Returns:
            Path to the saved file
        """
        processed_file = self._execute_operations()
        
        # Determine output path
        final_output = output_file or self._input_file
        
        # Copy processed file to final destination
        if processed_file != final_output:
            shutil.copy2(processed_file, final_output)
        
        # Cleanup temp files
        self._cleanup_temp_files()
        
        return final_output
    
    def to_json(self, output_file: Optional[str] = None) -> Dict:
        """
        Execute all operations and convert result to JSON.
        
        Args:
            output_file: Path to save JSON result
            
        Returns:
            Parsed JSON data as a dictionary. If output_file is provided, also saves to that file.
        """
        processed_file = self._execute_operations()
        
        # Convert to JSON
        json_data = self._tools.to_json(processed_file, output_file)
        
        # Cleanup temp files
        self._cleanup_temp_files()
        
        return json_data
    
    def __repr__(self) -> str:
        """String representation of processor."""
        ops = [f"{op}({kwargs})" for op, kwargs in self._operations]
        return f"SaveFileProcessor(file={self._input_file}, operations={ops})"
    
    def __enter__(self) -> 'SaveFileProcessor':
        """
        Enter context manager.
        
        Creates a temp directory and working copy of the input file.
        
        Returns:
            Self for use in with statement
            
        Example:
            >>> vst = ValheimSaveTools()
            >>> with vst.process("world.db") as processor:
            ...     processor.clean_structures().reset_world()
            ...     # Operations executed and cleaned up automatically
        """
        self._in_context = True
        
        # Create temp directory for working files
        self._temp_dir = tempfile.mkdtemp(prefix="valheim_processor_")
        
        # Copy input file to temp directory as working copy
        working_file = os.path.join(self._temp_dir, os.path.basename(self._input_file))
        shutil.copy2(self._input_file, working_file)
        self._current_file = working_file
        self._temp_files.append(working_file)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.
        
        If operations were queued, executes them and saves the result.
        Always cleans up temp files.
        
        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value if error occurred
            exc_tb: Exception traceback if error occurred
            
        Returns:
            False to propagate exceptions
        """
        try:
            # If no exception and operations were queued, execute them
            if exc_type is None and self._operations:
                # Execute operations on the working file
                for operation, kwargs in self._operations:
                    if operation == 'clean_structures':
                        self._tools.clean_structures(self._current_file, **kwargs)
                    elif operation == 'reset_world':
                        self._tools.reset_world(self._current_file)
                    elif operation == 'add_global_key':
                        self._tools.add_global_key(self._current_file, **kwargs)
                    elif operation == 'remove_global_key':
                        self._tools.remove_global_key(self._current_file, **kwargs)
                    elif operation == 'clear_all_global_keys':
                        self._tools.clear_all_global_keys(self._current_file)
                
                # Copy result back to original file
                shutil.copy2(self._current_file, self._input_file)
        finally:
            # Always cleanup temp files
            self._cleanup_temp_files()
            self._in_context = False
        
        # Return False to propagate any exceptions
        return False
    
    def _cleanup_temp_files(self):
        """Clean up temporary files and directory."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except (OSError, PermissionError):
                pass  # Best effort cleanup
        
        # Try to remove temp directory
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                if not os.listdir(self._temp_dir):
                    os.rmdir(self._temp_dir)
            except (OSError, PermissionError):
                pass  # Best effort cleanup
