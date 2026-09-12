"""`python -m webapp` starts the panel on http://127.0.0.1:8800."""

import argparse

from webapp.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Paneli i rezultateve të punimit")
    parser.add_argument("--host", default="127.0.0.1", help="ndërfaqja e lidhjes")
    parser.add_argument("--port", type=int, default=8800)
    parser.add_argument("--reload", action="store_true", help="rilexo kodin gjatë zhvillimit")
    args = parser.parse_args()
    print(f"Paneli: http://{args.host}:{args.port}")
    serve(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
