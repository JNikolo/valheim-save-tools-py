"""Wrapper for Valheim Save Tools JAR."""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List

from .exceptions import JarNotFoundError, JavaNotFoundError, CommandExecutionError


class ValheimSaveTools:
    """Python wrapper for Valheim Save Tools JAR file."""
    
    def __init__(self, jar_path: Optional[str] = None, java_path: Optional[str] = None):
        self.jar_path = self._find_jar(jar_path)
        self.java_path = self._find_java(java_path)
        
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
