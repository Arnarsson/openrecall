#!/usr/bin/env python3
"""
CLI entry point for OpenRecall with platform-aware execution.

Usage:
    openrecall              # Run with menu bar (macOS) or CLI mode (other platforms)
    openrecall --install    # Install auto-start at login (macOS only)
    openrecall --uninstall  # Remove auto-start
    openrecall --no-gui     # Run in CLI mode without menu bar
"""
import sys
import signal

from openrecall.config import get_args, appdata_folder


def main():
    """Main entry point for OpenRecall."""
    args = get_args()

    # Handle install/uninstall commands first
    if args.install or args.uninstall:
        if sys.platform != "darwin":
            print("Auto-start installation is only supported on macOS.")
            print("For other platforms, please use your system's startup manager.")
            sys.exit(1)

        from openrecall.launchagent import install_launchagent, uninstall_launchagent

        if args.install:
            success = install_launchagent()
        else:
            success = uninstall_launchagent()

        sys.exit(0 if success else 1)

    # Determine whether to run GUI or CLI mode
    use_gui = sys.platform == "darwin" and not args.no_gui

    if use_gui:
        try:
            from openrecall.menubar import run_menubar
            run_menubar(port=args.port)
        except ImportError as e:
            print(f"Menu bar not available: {e}")
            print("Falling back to CLI mode...")
            print("To install menu bar support, run: pip install rumps")
            run_cli_mode(port=args.port)
    else:
        run_cli_mode(port=args.port)


def run_cli_mode(port: int = 8082):
    """Run OpenRecall in traditional CLI mode (non-GUI)."""
    from openrecall.controller import OpenRecallController

    print("OpenRecall starting in CLI mode...")
    print(f"Data folder: {appdata_folder}")
    print(f"Dashboard: http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    print("")

    controller = OpenRecallController(port=port)

    # Set up graceful shutdown
    def signal_handler(signum, frame):
        print("\nShutting down...")
        controller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    controller.start()

    # Keep main thread alive
    try:
        # Use signal.pause() on Unix systems for efficient waiting
        while True:
            signal.pause()
    except AttributeError:
        # signal.pause() not available on Windows
        import time
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
