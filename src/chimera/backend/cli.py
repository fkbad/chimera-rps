import logging
import signal
import sys

import click
import asyncio
from importlib import import_module
from click_loglevel import LogLevel

from chimera.backend.websocket import WebSocketsChimeraServer


async def chimera_server(ws_server):
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, asyncio.create_task, ws_server.stop())

    await ws_server.start()
    await ws_server.wait_stopped()


def load_game_cls(full_cls_name):
    names = full_cls_name.split(".")
    module = ".".join(names[:-1])
    cls_name = names[-1]

    try:
        game_module = import_module(module)
    except ImportError:
        return None

    if not hasattr(game_module, cls_name):
        return None

    return getattr(game_module, cls_name)


@click.command(name="chimera-server")
@click.option('--addrport', type=click.STRING, default="127.0.0.1:14200")
@click.option('--load-game', type=click.STRING)
@click.option("--log-level", type=LogLevel(), default=logging.INFO)
def cmd(addrport, load_game, log_level):
    # TODO: Validate address and port
    host, port = addrport.split(":")

    if host == "*":
        host = None

    ws_server = WebSocketsChimeraServer(host, port)

    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
    chimera_logger = logging.getLogger("chimera")
    chimera_logger.setLevel(log_level)

    if load_game is not None:
        game_cls = load_game_cls(load_game)
        if game_cls is None:
            print(f"ERROR: No such class: {load_game}")
            sys.exit(1)

        class_name = game_cls.__name__
        ws_server.register_game(class_name.lower(), game_cls, class_name)

    asyncio.run(chimera_server(ws_server))


if __name__ == "__main__":
    cmd()
