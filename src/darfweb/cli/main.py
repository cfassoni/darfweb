import argparse
import os

from darfweb.core.sinacor import SinacorService

"""Minimal CLI entry point for darfweb.

This exposes a `cli` function that is referenced by the console script
entry in `pyproject.toml` (darf-cli = "darfweb.cli.main:cli").
"""


def cli() -> None:
    """Entry point for the darf-cli console script."""

    print("Welcome to DARF-web CLI!")

    parser = argparse.ArgumentParser(description='I\'m DARF-web "CLIller"!💥🔫')
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # sinacor subcommand
    sinacor_parser = subparsers.add_parser("sinacor", help="Handle Sinacor Statements")
    sinacor_parser.add_argument("filename", help="Path to Sinacor statement file")
    sinacor_parser.add_argument(
        "-d",
        "--detect",
        action="store_true",
        help="Detect brokers and brokerage notes types",
        default=True,
    )
    sinacor_parser.add_argument(
        "-e",
        "--extract",
        action="store_true",
        help="Extract data from Sinacor Statement to JSON",
        default=False,
    )
    sinacor_parser.add_argument(
        "-o",
        "--output",
        help="Output file for extracted JSON data (optional)",
        default=None,
    )
    sinacor_parser.add_argument(
        "-v",
        "--view",
        action="store_true",
        help="Visualize Sinacor Statement",
        default=False,
    )

    args = parser.parse_args()

    if args.command == "sinacor":
        handle_sinacor(args)
    else:
        parser.print_help()


def handle_sinacor(args: argparse.Namespace) -> None:
    """Handle the 'sinacor' subcommand."""
    full_filename = args.filename

    filepath = os.path.abspath(full_filename)
    filename = os.path.basename(filepath)

    try:
        if not os.path.exists(full_filename):
            raise FileNotFoundError(f"File not found: {filename}")

        if not args.output:
            args.output = os.path.splitext(args.filename)[0] + ".json"

        print(f"Validating file {filename}...", end="")
        sinacor_service = SinacorService(full_filename, autodetect=args.detect)
        print(f"done. File has {sinacor_service.num_pages} page(s).")

        if args.detect and sinacor_service.is_detected:
            print("Detected broker and note type:")
            for page in sinacor_service.detected:
                print(
                    f"    Page {page.get('page', 'N/A')}: Broker: {page.get('brokerAlias', 'N/A')}, Type: {page.get('invoiceType', 'N/A')}"
                )
        if args.extract:
            print(f"Extracting data from {filename} to JSON...")
            output_file = args.output or "output.json"
            print(f"Output will be saved to {output_file}")
            # Placeholder for extraction logic
        if args.view:
            print(f"Visualizing Sinacor Statement from {filename}...\n")
            # Placeholder for visualization logic
            for page in sinacor_service.pages:
                text = page.extract_text().lower()
                print(f"--- Page {sinacor_service.pages.index(page) + 1} ---")
                print(text)
                print("-------------------------\n")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    cli()
