"""
ConfigService - Configuration and settings management.

This service handles all configuration logic,
decoupled from any UI layer (GUI or CLI).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal


class ConfigService:
    """
    Core service for configuration management.
    
    This service is UI-agnostic and can be used by both GUI and CLI.
    """
    
    CONFIG_FILE = Path.home() / ".cartographer" / "config.json"
    
    def __init__(self):
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def get_config(self) -> dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Dictionary containing all configuration settings
        """
        if not self.CONFIG_FILE.exists():
            return self._default_config()
        
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            return {**self._default_config(), **config}
        except Exception:
            return self._default_config()
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot-notation supported, e.g., 'llm.provider')
            value: Configuration value
        """
        config = self.get_config()
        
        # Handle dot notation for nested keys
        if "." in key:
            parts = key.split(".")
            current = config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            config[key] = value
        
        self._save_config(config)
    
    def get_llm_config(self) -> dict[str, Any]:
        """Get LLM configuration."""
        config = self.get_config()
        return config.get("llm", {})
    
    def set_llm_provider(
        self,
        provider: Literal["gemini", "openai"],
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """
        Configure LLM provider.
        
        Args:
            provider: LLM provider name
            api_key: API key (optional, can use env var)
            model: Model name (optional, uses default)
        """
        config = self.get_config()
        
        if "llm" not in config:
            config["llm"] = {}
        
        config["llm"]["provider"] = provider
        
        if api_key:
            config["llm"]["api_key"] = api_key
        
        if model:
            config["llm"]["model"] = model
        elif provider == "gemini":
            config["llm"]["model"] = "gemini-2.0-flash-exp"
        elif provider == "openai":
            config["llm"]["model"] = "gpt-4"
        
        self._save_config(config)
    
    def get_language_config(self) -> dict[str, Any]:
        """Get language analysis configuration."""
        config = self.get_config()
        return config.get("languages", {})
    
    def set_language_enabled(self, language: str, enabled: bool) -> None:
        """
        Enable or disable analysis for a specific language.
        
        Args:
            language: Language name (e.g., 'python', 'javascript', 'sql')
            enabled: Whether to enable analysis for this language
        """
        config = self.get_config()
        
        if "languages" not in config:
            config["languages"] = {}
        
        config["languages"][language] = enabled
        self._save_config(config)
    
    def get_analysis_config(self) -> dict[str, Any]:
        """Get analysis configuration."""
        config = self.get_config()
        return config.get("analysis", {})
    
    def set_analysis_option(self, option: str, value: Any) -> None:
        """
        Set an analysis option.
        
        Args:
            option: Option name (e.g., 'incremental', 'max_file_size')
            value: Option value
        """
        config = self.get_config()
        
        if "analysis" not in config:
            config["analysis"] = {}
        
        config["analysis"][option] = value
        self._save_config(config)
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self._save_config(self._default_config())
    
    def export_config(self, output_path: Path | str) -> None:
        """
        Export configuration to a file.
        
        Args:
            output_path: Path to export configuration
        """
        config = self.get_config()
        output_path = Path(output_path)
        
        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)
    
    def import_config(self, input_path: Path | str) -> None:
        """
        Import configuration from a file.
        
        Args:
            input_path: Path to import configuration from
        """
        input_path = Path(input_path)
        
        with open(input_path, "r") as f:
            config = json.load(f)
        
        self._save_config(config)
    
    def _default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "llm": {
                "provider": "gemini",
                "model": "gemini-2.0-flash-exp",
                "api_key": os.getenv("GEMINI_API_KEY", ""),
            },
            "languages": {
                "python": True,
                "javascript": True,
                "typescript": True,
                "sql": True,
                "java": True,
                "go": True,
            },
            "analysis": {
                "incremental": True,
                "max_file_size_kb": 1024,
                "exclude_patterns": [
                    ".git",
                    ".venv",
                    "node_modules",
                    "__pycache__",
                    "*.pyc",
                ],
            },
            "output": {
                "artifacts_dir": ".cartography",
                "generate_html": True,
                "generate_markdown": True,
            },
        }
    
    def _save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
