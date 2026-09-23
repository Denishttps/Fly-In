import argparse
import uvicorn  # type: ignore[import-not-found]

from dispatcher import Dispatcher
from app import app

from typing import Any


def init_app(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    **kwargs: dict[str, Any]
) -> None:
    uvicorn.run(app, host=host, port=port, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser("Fly-In")

    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default="",
        help="Path to file with map"
    )

    parser.add_argument(
        "-w",
        "--web",
        action="store_true",
        help="Enable web interface"
    )

    args = parser.parse_args()

    if args.web:
        init_app()
    else:
        if not args.path:
            parser.error("Missing argument: --path")
        dp = Dispatcher(args.path)
        dp.print_simulation()


if __name__ == "__main__":
    main()
