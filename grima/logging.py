import inspect
import logging
import os
import sys
from typing import Any, Dict

import __main__
import structlog

log_level: str = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.getLevelName(log_level.upper()),
)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def add_code_info(logger: logging.Logger, method_name: str, event_dict: Any) -> Dict[str, Any]:
    frame = inspect.currentframe().f_back.f_back.f_back.f_back.f_back  # type: ignore
    event_dict["func"] = frame.f_code.co_name  # type: ignore
    fname: str = frame.f_code.co_filename.replace(root_dir, "").lstrip("/")  # type: ignore
    event_dict["file"] = f"{fname}:{frame.f_lineno}"  # type: ignore
    return event_dict


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_code_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.EventRenamer(to="msg"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def init():
    # the work is done on load
    return None