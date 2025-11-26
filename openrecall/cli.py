#!/usr/bin/env python3
"""
CLI entry point for OpenRecall with platform-aware execution.

Usage:
    openrecall              # Run with menu bar (macOS) or CLI mode (other platforms)
    openrecall --install    # Install auto-start at login (macOS only)
    openrecall --uninstall  # Remove auto-start
    openrecall --no-gui     # Run in CLI mode without menu bar
    openrecall --export-memories  # Export to Universal Memory MCP
    openrecall --sync-memories    # Run with real-time Universal Memory sync
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

    # Handle Universal Memory export
    if args.export_memories:
        export_to_universal_memory(args.mcp_url)
        sys.exit(0)

    # Determine whether to run GUI or CLI mode
    use_gui = sys.platform == "darwin" and not args.no_gui

    # Check if real-time sync is enabled
    sync_memories = args.sync_memories
    mcp_url = args.mcp_url

    if use_gui:
        try:
            from openrecall.menubar import run_menubar
            run_menubar(port=args.port, sync_memories=sync_memories, mcp_url=mcp_url)
        except ImportError as e:
            print(f"Menu bar not available: {e}")
            print("Falling back to CLI mode...")
            print("To install menu bar support, run: pip install rumps")
            run_cli_mode(port=args.port, sync_memories=sync_memories, mcp_url=mcp_url)
    else:
        run_cli_mode(port=args.port, sync_memories=sync_memories, mcp_url=mcp_url)


def export_to_universal_memory(mcp_url: str):
    """Export all OpenRecall data to Universal Memory."""
    print("Exporting OpenRecall data to Universal Memory...")
    print(f"MCP URL: {mcp_url}")
    print("")

    try:
        from openrecall.universal_memory import export_to_universal_memory as do_export
        results = do_export(mcp_url=mcp_url)

        if "error" in results:
            print(f"Error: {results['error']}")
            sys.exit(1)

    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Install with: pip install requests")
        sys.exit(1)
    except Exception as e:
        print(f"Export failed: {e}")
        sys.exit(1)


def run_cli_mode(port: int = 8082, sync_memories: bool = False, mcp_url: str = "http://localhost:3000"):
    """Run OpenRecall in traditional CLI mode (non-GUI)."""
    from openrecall.controller import OpenRecallController

    print("OpenRecall starting in CLI mode...")
    print(f"Data folder: {appdata_folder}")
    print(f"Dashboard: http://localhost:{port}")
    if sync_memories:
        print(f"Universal Memory sync: ENABLED ({mcp_url})")
    print("Press Ctrl+C to stop.")
    print("")

    controller = OpenRecallController(port=port, sync_memories=sync_memories, mcp_url=mcp_url)

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
