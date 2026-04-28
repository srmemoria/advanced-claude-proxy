import os
import importlib.util
from loguru import logger
from typing import Any, Dict

class PluginManager:
    """Discovers and executes local python scripts as Claude Tools."""
    
    def __init__(self, plugins_dir: str = "src/plugins/custom"):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self._load_plugins()

    def _load_plugins(self):
        """Dynamically loads all .py files in the plugins directory."""
        os.makedirs(self.plugins_dir, exist_ok=True)
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                filepath = os.path.join(self.plugins_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "execute") and hasattr(module, "TOOL_SCHEMA"):
                        self.plugins[plugin_name] = module
                        logger.info(f"Loaded custom plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def get_tool_schemas(self) -> list[Dict[str, Any]]:
        """Returns the Anthropic tool schemas for all loaded plugins."""
        return [plugin.TOOL_SCHEMA for plugin in self.plugins.values()]

    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Any:
        """Executes a local plugin."""
        if tool_name in self.plugins:
            try:
                logger.info(f"Executing local plugin: {tool_name}")
                return self.plugins[tool_name].execute(**input_data)
            except Exception as e:
                logger.error(f"Plugin {tool_name} failed: {e}")
                return f"Error: {e}"
        return None

plugin_manager = PluginManager()
