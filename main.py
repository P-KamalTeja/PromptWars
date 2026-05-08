"""Main application entry point."""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import Config, get_logger
from src.ui import GradioUI, WebUI


logger = get_logger(__name__)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="AI Travel Planning Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ui web                 # Start web UI
  python main.py --ui gradio              # Start Gradio UI
  python main.py --ui web --debug         # Start web UI in debug mode
  python main.py --ui gradio --share      # Share Gradio interface
        """,
    )

    parser.add_argument(
        "--ui",
        choices=["web", "gradio"],
        default="web",
        help="UI type to launch (default: web)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Server port (default: 8080)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Share Gradio interface (Gradio only)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config.from_env()

        if args.debug:
            config.DEBUG = True

        logger.info(f"Starting AI Travel Platform - {config.APP_VERSION}")

        # Launch UI
        if args.ui == "web":
            logger.info("Launching Web UI...")
            ui = WebUI(config)
            ui.run(host=args.host, port=args.port, debug=args.debug)

        elif args.ui == "gradio":
            logger.info("Launching Gradio UI...")
            ui = GradioUI(config)
            ui.launch(
                share=args.share,
                server_name=args.host,
                server_port=args.port,
            )

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
