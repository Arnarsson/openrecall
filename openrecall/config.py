import os
import sys
import argparse

# Lazy-loaded configuration
_args = None
_appdata_folder = None
_db_path = None
_screenshots_path = None


def create_parser():
    """Create the argument parser with all CLI options."""
    parser = argparse.ArgumentParser(description="OpenRecall - Take Control of Your Digital Memory")

    parser.add_argument(
        "--storage-path",
        default=None,
        help="Path to store the screenshots and database",
    )

    parser.add_argument(
        "--primary-monitor-only",
        action="store_true",
        help="Only record the primary monitor",
        default=False,
    )

    parser.add_argument(
        "--install",
        action="store_true",
        help="Install auto-start (macOS LaunchAgent)",
    )

    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove auto-start",
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in CLI mode without menu bar",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="Port for web dashboard (default: 8082)",
    )

    # Universal Memory integration
    parser.add_argument(
        "--export-memories",
        action="store_true",
        help="Export all captures to Universal Memory MCP",
    )

    parser.add_argument(
        "--sync-memories",
        action="store_true",
        help="Enable real-time sync to Universal Memory MCP",
    )

    parser.add_argument(
        "--mcp-url",
        default="http://localhost:3000",
        help="Universal Memory MCP server URL (default: http://localhost:3000)",
    )

    return parser


def get_args(argv=None):
    """Parse and return command line arguments. Cached after first call."""
    global _args
    if _args is None:
        parser = create_parser()
        _args = parser.parse_args(argv)
    return _args


def get_appdata_folder(app_name="openrecall"):
    """Get the platform-specific application data folder."""
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise EnvironmentError("APPDATA environment variable is not set.")
        path = os.path.join(appdata, app_name)
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        path = os.path.join(home, "Library", "Application Support", app_name)
    else:
        home = os.path.expanduser("~")
        path = os.path.join(home, ".local", "share", app_name)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _init_paths():
    """Initialize all paths based on args. Called lazily."""
    global _appdata_folder, _db_path, _screenshots_path

    args = get_args()

    if args.storage_path:
        _appdata_folder = args.storage_path
    else:
        _appdata_folder = get_appdata_folder()

    _db_path = os.path.join(_appdata_folder, "recall.db")
    _screenshots_path = os.path.join(_appdata_folder, "screenshots")

    if not os.path.exists(_screenshots_path):
        try:
            os.makedirs(_screenshots_path)
        except:
            pass


# Properties for lazy access (backward compatibility)
class _ConfigProxy:
    """Proxy class for lazy configuration access."""

    @property
    def primary_monitor_only(self):
        return get_args().primary_monitor_only

    @property
    def storage_path(self):
        return get_args().storage_path

    @property
    def install(self):
        return get_args().install

    @property
    def uninstall(self):
        return get_args().uninstall

    @property
    def no_gui(self):
        return get_args().no_gui

    @property
    def port(self):
        return get_args().port


# Backward compatibility: 'args' object with lazy loading
args = _ConfigProxy()


# Lazy path properties
def _get_appdata_folder():
    global _appdata_folder
    if _appdata_folder is None:
        _init_paths()
    return _appdata_folder


def _get_db_path():
    global _db_path
    if _db_path is None:
        _init_paths()
    return _db_path


def _get_screenshots_path():
    global _screenshots_path
    if _screenshots_path is None:
        _init_paths()
    return _screenshots_path


# Module-level properties for backward compatibility
# These are accessed as config.appdata_folder, config.db_path, etc.
class _PathsModule:
    @property
    def appdata_folder(self):
        return _get_appdata_folder()

    @property
    def db_path(self):
        return _get_db_path()

    @property
    def screenshots_path(self):
        return _get_screenshots_path()


# Use __getattr__ for module-level lazy loading (Python 3.7+)
# This allows config.appdata_folder, config.db_path, etc. to work lazily
def __getattr__(name):
    if name == "appdata_folder":
        return _get_appdata_folder()
    elif name == "db_path":
        return _get_db_path()
    elif name == "screenshots_path":
        return _get_screenshots_path()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
