from uvicorn.workers import UvicornWorker as BaseUvicornWorker

class UvicornWorker(BaseUvicornWorker):
    CONFIG_KWARGS = {
        "loop": "uvloop",
        "http": "httptools",
        "lifespan": "off",
        "ws_ping_interval": None,
        "ws_ping_timeout": None,
        "log_level": "debug"
    }
