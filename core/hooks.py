import pluggy

hookspec = pluggy.HookspecMarker("sh")
hookimpl = pluggy.HookimplMarker("sh")

class PluginSpec:
    """
    Plugin system hook specifications.
    """
    @hookspec
    def sh_plugin_init(self, registry):
        """
        Called during plugin initialization.
        Plugins should use this to register their capabilities.
        """
