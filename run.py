import argparse
import sys

from portal import create_app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="rebuild the seed data and exit")
    ap.add_argument("--port", type=int, default=5002)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    if args.host not in ("127.0.0.1", "localhost"):
        print("This app is vulnerable on purpose and binds to 127.0.0.1 only.")
        sys.exit(2)
    app = create_app()
    if args.reset:
        from portal.seed import seed
        with app.app_context():
            seed()
        print("Seed data rebuilt.")
        return
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
