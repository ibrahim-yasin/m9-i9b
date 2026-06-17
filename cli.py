from __future__ import annotations

import os
import sys
from neo4j import GraphDatabase

from mapper import UnsupportedQueryError
from pipeline import answer

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "testtest")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python cli.py \"question\"")
        return 2

    question = argv[1]

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    try:
        rows = answer(driver, question)

        if not rows:
            print("(no results)")
        else:
            for row in rows:
                print(row)

        return 0

    except UnsupportedQueryError as e:
        print(str(e), file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2

    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))