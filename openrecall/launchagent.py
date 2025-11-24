"""
macOS LaunchAgent management for OpenRecall auto-start functionality.
"""
import os
import sys
import plistlib
import subprocess
from pathlib import Path

LAUNCHAGENT_LABEL = "com.openrecall.agent"
LAUNCHAGENT_FILENAME = f"{LAUNCHAGENT_LABEL}.plist"


def get_launchagent_path() -> Path:
    """Get the path to the LaunchAgent plist file."""
    return Path.home() / "Library" / "LaunchAgents" / LAUNCHAGENT_FILENAME


def get_log_path() -> Path:
    """Get the path to the log directory."""
    return Path.home() / "Library" / "Logs"


def get_plist_content() -> dict:
    """Generate LaunchAgent plist configuration."""
    python_path = sys.executable
    log_path = get_log_path()

    return {
        "Label": LAUNCHAGENT_LABEL,
        "ProgramArguments": [
            python_path,
            "-m",
            "openrecall.cli",
        ],
        "RunAtLoad": True,
        "KeepAlive": {
            "SuccessfulExit": False,  # Restart if exits with error
        },
        "StandardOutPath": str(log_path / "openrecall.log"),
        "StandardErrorPath": str(log_path / "openrecall.error.log"),
        "ProcessType": "Interactive",  # Required for screen recording permissions
        "EnvironmentVariables": {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        },
    }


def install_launchagent() -> bool:
    """
    Install the LaunchAgent plist file for auto-start at login.

    Returns:
        True if installation was successful, False otherwise.
    """
    if sys.platform != "darwin":
        print("Error: LaunchAgent is only supported on macOS.")
        return False

    try:
        plist_path = get_launchagent_path()

        # Ensure LaunchAgents directory exists
        plist_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure Logs directory exists
        get_log_path().mkdir(parents=True, exist_ok=True)

        # Unload existing agent if present
        if plist_path.exists():
            subprocess.run(
                ["launchctl", "unload", str(plist_path)],
                capture_output=True,
            )

        # Write plist file
        plist_content = get_plist_content()
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        # Load the agent
        result = subprocess.run(
            ["launchctl", "load", str(plist_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Warning: launchctl load returned: {result.stderr}")

        print(f"LaunchAgent installed at: {plist_path}")
        print("OpenRecall will now start automatically at login.")
        print("")
        print("Note: You may need to grant Screen Recording permission in:")
        print("  System Preferences > Security & Privacy > Privacy > Screen Recording")
        return True

    except Exception as e:
        print(f"Failed to install LaunchAgent: {e}")
        return False


def uninstall_launchagent() -> bool:
    """
    Remove the LaunchAgent plist file to disable auto-start.

    Returns:
        True if uninstallation was successful, False otherwise.
    """
    if sys.platform != "darwin":
        print("Error: LaunchAgent is only supported on macOS.")
        return False

    try:
        plist_path = get_launchagent_path()

        if plist_path.exists():
            # Unload first
            subprocess.run(
                ["launchctl", "unload", str(plist_path)],
                capture_output=True,
            )

            # Remove file
            plist_path.unlink()

            print(f"LaunchAgent removed: {plist_path}")
            print("OpenRecall will no longer start automatically.")
            return True
        else:
            print("LaunchAgent not installed.")
            return True

    except Exception as e:
        print(f"Failed to uninstall LaunchAgent: {e}")
        return False


def is_launchagent_installed() -> bool:
    """Check if LaunchAgent is currently installed."""
    return get_launchagent_path().exists()


def get_launchagent_status() -> str:
    """Get the current status of the LaunchAgent."""
    if not is_launchagent_installed():
        return "not installed"

    try:
        result = subprocess.run(
            ["launchctl", "list", LAUNCHAGENT_LABEL],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "running"
        else:
            return "installed but not running"
    except Exception:
        return "unknown"
