import argparse
import uvicorn

from dispatcher import Dispatcher
from app import app


def init_app(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    **kwargs
) -> None:
    uvicorn.run(app, host=host, port=port, reload=reload, **kwargs)


def main():
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
            raise argparse.ArgumentError()
        dp = Dispatcher(args.path)
        dp.print_simulation()


if __name__ == "__main__":
    main()
