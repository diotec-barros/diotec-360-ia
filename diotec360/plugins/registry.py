"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Aethel Plugin Registry

Central registry for managing all AI plugins
"""

from typing import Dict, List, Optional
from .base import AethelPlugin, PluginResult


class AethelPluginRegistry:
    """
    Central registry for all AI plugins
    
    Manages plugin lifecycle:
    - Registration
    - Execution
    - Monitoring
    - Statistics
    
    Example:
        registry = AethelPluginRegistry()
        registry.register("llm", LLMPlugin("gpt-4"))
        result = registry.execute("llm", {"input": "Transfer $100"})
    """
    
    def __init__(self):
        """Initialize plugin registry"""
        self.plugins: Dict[str, AethelPlugin] = {}
        self.execution_history: List[PluginResult] = []
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
    
    def register(self, name: str, plugin: AethelPlugin) -> None:
        """
        Register a new AI plugin
        
        Args:
            name: Unique plugin name
            plugin: Plugin instance
        
        Example:
            registry.register("my_ai", MyAIPlugin())
        """
        if name in self.plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        
        self.plugins[name] = plugin
        print(f"✓ Registered plugin: {name} (v{plugin.version})")
    
    def unregister(self, name: str) -> None:
        """
        Unregister a plugin
        
        Args:
            name: Plugin name to remove
        """
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found")
        
        del self.plugins[name]
        print(f"✓ Unregistered plugin: {name}")
    
    def execute(
        self,
        plugin_name: str,
        context: Dict,
        record_history: bool = True
    ) -> PluginResult:
        """
        Execute AI action with Aethel supervision
        
        Args:
            plugin_name: Name of plugin to execute
            context: Input context for AI
            record_history: Whether to record in history
        
        Returns:
            PluginResult with execution details
        
        Example:
            result = registry.execute("llm", {
                "input": "Transfer $100 with 2% fee"
            })
            if result.success:
                print(result.output)
        """
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        
        plugin = self.plugins[plugin_name]
        
        # Execute plugin pipeline
        result = plugin.run(context)
        
        # Update statistics
        self.stats["total_executions"] += 1
        if result.success:
            self.stats["successful_executions"] += 1
        else:
            self.stats["failed_executions"] += 1
        
        # Record history
        if record_history:
            self.execution_history.append(result)
            # Keep only last 1000 executions
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
        
        return result
    
    def list_plugins(self) -> List[Dict]:
        """
        List all registered plugins
        
        Returns:
            List of plugin info dictionaries
        """
        return [
            {
                "name": name,
                "version": plugin.version,
                "stats": plugin.get_stats()
            }
            for name, plugin in self.plugins.items()
        ]
    
    def get_plugin(self, name: str) -> Optional[AethelPlugin]:
        """
        Get plugin by name
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            **self.stats,
            "registered_plugins": len(self.plugins),
            "success_rate": self._calculate_success_rate(),
            "plugin_stats": {
                name: plugin.get_stats()
                for name, plugin in self.plugins.items()
            }
        }
    
    def get_history(self, limit: int = 100) -> List[PluginResult]:
        """
        Get execution history
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of recent plugin results
        """
        return self.execution_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear execution history"""
        self.execution_history = []
        print("✓ Execution history cleared")
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = self.stats["total_executions"]
        if total == 0:
            return 0.0
        successful = self.stats["successful_executions"]
        return successful / total


# Global registry instance
_global_registry = None


def get_global_registry() -> AethelPluginRegistry:
    """Get global plugin registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AethelPluginRegistry()
    return _global_registry


def register_plugin(name: str, plugin: AethelPlugin) -> None:
    """Register plugin in global registry"""
    registry = get_global_registry()
    registry.register(name, plugin)


def execute_plugin(plugin_name: str, context: Dict) -> PluginResult:
    """Execute plugin from global registry"""
    registry = get_global_registry()
    return registry.execute(plugin_name, context)
