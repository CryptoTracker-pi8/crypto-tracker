"""
Common FastAPI dependencies shared across multiple routers.
"""

from typing import Annotated

from fastapi import Header, HTTPException, status


def get_current_user_id(
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None,
) -> int:
    """
    Resolve the current authenticated user ID from the ``X-User-Id`` header.

    The project does not yet include a dedicated authentication provider,
    therefore a simple header-based approach is used to keep the examples
    deterministic. A 401 error is raised when the header is missing.
    """

    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header.",
        )
    return x_user_id

