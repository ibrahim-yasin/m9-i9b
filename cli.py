"""CLI entry point for the recipe KG NL → Cypher pipeline."""

import argparse
import json
import os
import sys

from neo4j import GraphDatabase

from mapper import UnsupportedQueryError
from pipeline import answer


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
    )
    parser.add_argument(
        "--user",
        default=os.getenv("NEO4J_USER", "neo4j"),
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD", "testtest"),
    )

    args = parser.parse_args(argv[1:])

    driver = GraphDatabase.driver(
        args.uri,
        auth=(args.user, args.password),
    )

    try:
        rows = answer(driver, args.question)
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    except UnsupportedQueryError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))