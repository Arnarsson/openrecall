"""
macOS menu bar application for OpenRecall using rumps.

This module provides a native macOS menu bar icon with controls for:
- Opening the web dashboard
- Pausing/resuming screenshot recording
- Quitting the application
"""
import sys
import webbrowser

# Only import rumps on macOS
if sys.platform == "darwin":
    try:
        import rumps
        RUMPS_AVAILABLE = True
    except ImportError:
        RUMPS_AVAILABLE = False
else:
    RUMPS_AVAILABLE = False

from openrecall.controller import OpenRecallController
from openrecall.config import appdata_folder


class OpenRecallMenuBar(rumps.App):
    """
    macOS menu bar application for OpenRecall.

    Provides a status bar icon with menu items to control the application.
    """

    def __init__(self, controller: OpenRecallController, port: int = 8082):
        # Use a simple text indicator (emoji works well in menu bar)
        super().__init__(
            name="OpenRecall",
            title="OR",  # Text shown in menu bar
            quit_button=None,  # We'll handle quit ourselves
        )
        self.controller = controller
        self.port = port

        # Build menu
        self.menu = [
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            None,  # Separator
            rumps.MenuItem("Pause Recording", callback=self.toggle_recording),
            None,  # Separator
            rumps.MenuItem("Quit OpenRecall", callback=self.quit_app),
        ]

        # Update initial status
        self._update_status()

    def _update_status(self):
        """Update menu bar title and menu items to reflect current state."""
        if self.controller.is_recording:
            self.title = "OR"  # Normal state
            self.menu["Pause Recording"].title = "Pause Recording"
        else:
            self.title = "OR (Paused)"  # Paused indicator
            self.menu["Pause Recording"].title = "Resume Recording"

    def open_dashboard(self, _):
        """Open the web dashboard in the default browser."""
        url = f"http://localhost:{self.port}"
        webbrowser.open(url)

    def toggle_recording(self, sender):
        """Toggle between paused and recording states."""
        if self.controller.is_recording:
            self.controller.pause_recording()
        else:
            self.controller.resume_recording()
        self._update_status()

    def quit_app(self, _):
        """Stop all services and quit the application."""
        self.controller.stop()
        rumps.quit_application()


def run_menubar(port: int = 8082, sync_memories: bool = False, mcp_url: str = "http://localhost:3000"):
    """
    Entry point for the menu bar application.

    Args:
        port: Port number for the web dashboard.
        sync_memories: Enable real-time sync to Universal Memory.
        mcp_url: Universal Memory MCP server URL.
    """
    if not RUMPS_AVAILABLE:
        raise ImportError(
            "rumps is not available. Install it with: pip install rumps"
        )

    print(f"OpenRecall starting...")
    print(f"Data folder: {appdata_folder}")
    print(f"Dashboard: http://localhost:{port}")
    if sync_memories:
        print(f"Universal Memory sync: ENABLED ({mcp_url})")
    print("")

    # Create and start controller
    controller = OpenRecallController(port=port, sync_memories=sync_memories, mcp_url=mcp_url)
    controller.start()

    # Create and run menu bar app
    app = OpenRecallMenuBar(controller, port=port)

    try:
        app.run()
    finally:
        controller.stop()


if __name__ == "__main__":
    run_menubar()
