"""
Central controller for managing OpenRecall application state and threads.
"""
import threading
from typing import Optional


class OpenRecallController:
    """
    Manages the lifecycle of OpenRecall services including:
    - Screenshot recording thread
    - Flask web server thread
    - Pause/resume functionality
    - Graceful shutdown
    """

    def __init__(self, port: int = 8082):
        self.port = port
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.screenshot_thread: Optional[threading.Thread] = None
        self.flask_thread: Optional[threading.Thread] = None
        self._started = False

    def start(self):
        """Start all OpenRecall services (database, screenshot recording, web server)."""
        if self._started:
            return

        from openrecall.database import create_db
        from openrecall.screenshot import record_screenshots_thread

        # Initialize database
        create_db()

        # Clear any previous stop signals
        self.stop_event.clear()
        self.pause_event.clear()

        # Start screenshot recording thread
        self.screenshot_thread = threading.Thread(
            target=record_screenshots_thread,
            args=(self.stop_event, self.pause_event),
            daemon=True,
            name="ScreenshotRecorder",
        )
        self.screenshot_thread.start()

        # Start Flask web server in background thread
        self.flask_thread = threading.Thread(
            target=self._run_flask,
            daemon=True,
            name="FlaskServer",
        )
        self.flask_thread.start()

        self._started = True

    def _run_flask(self):
        """Run Flask server (called in a thread)."""
        from openrecall.app import app

        # Disable Flask's reloader in threaded mode
        app.run(port=self.port, use_reloader=False, threaded=True)

    def stop(self):
        """Stop all services gracefully."""
        if not self._started:
            return

        # Signal threads to stop
        self.stop_event.set()

        # Wait for screenshot thread to finish
        if self.screenshot_thread and self.screenshot_thread.is_alive():
            self.screenshot_thread.join(timeout=5)

        # Flask thread is daemon, will stop with main process
        self._started = False

    def pause_recording(self):
        """Pause screenshot recording."""
        self.pause_event.set()

    def resume_recording(self):
        """Resume screenshot recording."""
        self.pause_event.clear()

    @property
    def is_recording(self) -> bool:
        """Check if screenshot recording is active (not paused)."""
        return self._started and not self.pause_event.is_set()

    @property
    def is_running(self) -> bool:
        """Check if the controller has been started."""
        return self._started
