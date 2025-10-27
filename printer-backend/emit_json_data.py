# Import required modules
import time  # Provides time-related functions like sleep to introduce delays
import json  # Enables working with JSON data
import argparse  # Allows handling command-line arguments
import sys
from pathlib import Path

try:
    import importlib
    # Import boto3 dynamically to avoid static analyzers failing when the package is not installed.
    boto3 = importlib.import_module("boto3")
except ImportError:
    boto3 = None  # type: ignore

# Function to emit JSON data to an AWS IoT topic
def emit_json_to_iot(topic: str, json_file: str, dry_run: bool = False) -> None:
    """Read a JSON file and publish each entry to an AWS IoT topic.

    Args:
        topic: AWS IoT topic (e.g., "anom/detect").
        json_file: Path to a JSON file containing a list of observations.
        dry_run: If True, do not call AWS; just print what would be sent.

    Raises:
        RuntimeError: if boto3 is required but not installed.
        FileNotFoundError: if `json_file` doesn't exist.
        json.JSONDecodeError: if the file is not valid JSON.
    """

    path = Path(json_file)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_file}")

    # Load JSON data (expecting a list of observations)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array (list) in {json_file}")

    # If user requested a dry run, just print the payloads instead of publishing
    if dry_run:
        for observation in data:
            print("[dry-run] Emitted observation:", json.dumps(observation))
            time.sleep(0.30)
        return

    # Ensure boto3 is available for real publishes
    if boto3 is None:
        raise RuntimeError(
            "boto3 is required to publish to AWS IoT. Install it with: python -m pip install boto3"
        )

    # Create an AWS IoT Data client and publish each observation
    client = boto3.client("iot-data")
    for observation in data:
        client.publish(topic=topic, qos=1, payload=json.dumps(observation))
        time.sleep(0.30)
        print("Emitted observation:", observation)

# Main block to handle command-line arguments and run the script
if __name__ == '__main__':
    # Creates an argument parser for parsing command-line arguments.
    parser = argparse.ArgumentParser()

    # Defines two required command-line arguments
    # - topic: The AWS IoT topic to publish messages to
    # - json_file: The path to the JSON file containing the data to emit
    parser.add_argument("topic", help="The IoT topic to publish to (e.g., anom/detect)")
    parser.add_argument("json_file", help="The JSON file containing data to send to AWS IoT")

    # Add a --dry-run flag so users can test locally without AWS credentials/boto3
    parser.add_argument(
        "--dry-run", action="store_true", help="Print messages instead of publishing to AWS IoT"
    )
    args = parser.parse_args()

    try:
        emit_json_to_iot(args.topic, args.json_file, dry_run=args.dry_run)
    except Exception as exc:  # keep broad for friendly CLI output
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)