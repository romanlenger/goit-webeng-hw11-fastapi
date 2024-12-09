from typing import Callable, Optional, Any, Tuple, Dict
from fastapi import Request, Response


def key_builder_repo(
        func: Callable[..., Any],
        namespace: str = "",
        *,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
) -> str:
    key_parts = [namespace, func.__name__] + [str(param) for param in args[1:]]
    return ":".join(key_parts)