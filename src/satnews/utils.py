import argparse
import json
import lzma
from itertools import islice
from pathlib import Path


def get_parser(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        required=True,
        help="The path to extracted articles compressed json file."
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="This limits the number of articles that will be processed."
    )
    return parser


def module_wrapper(args, output_file_name, input_file_name, run_module):
    path = Path(args.path)
    stem = path.stem

    with lzma.open(path.parent / (stem + input_file_name), "rb") as file:
        input_data = json.loads(file.read().decode("utf-8"))
    limit = len(input_data) if args.limit is None else args.limit
    input_data = dict(islice(input_data.items(), 0, limit))
    result = run_module(input_data, args)
    with lzma.open(path.parent / (stem + output_file_name), "wb") as file:
        file.write(json.dumps(result).encode("utf-8"))
