import logging
from datetime import datetime
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import List

from app.config import SECRET_KEY, ALGORITHM

auth_middleware_logger = logging.getLogger("dreamfit_api.auth_middleware")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def require_roles(allowed_roles: List[str]):
    async def role_checker(token: str = Depends(oauth2_scheme), request: Request = None):
        client_ip = request.client.host if request and request.client else "unknown"
        endpoint = request.url.path if request else "unknown"
        method = request.method if request else "unknown"

        auth_middleware_logger.debug(
            f"AUTH_CHECK_START | Endpoint: {method} {endpoint} | IP: {client_ip}"
        )

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            auth_middleware_logger.debug("DECODING_JWT_TOKEN")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user_role: str = payload.get("role")
            exp = payload.get("exp")
            logged_user_id = payload.get("userId")
            email = payload.get("sub")

            if exp is None:
                auth_middleware_logger.warning(
                    f"TOKEN_NO_EXPIRATION | IP: {client_ip} | Endpoint: {endpoint}"
                )
                raise credentials_exception

            if datetime.fromtimestamp(exp) < datetime.now():
                auth_middleware_logger.warning(
                    f"TOKEN_EXPIRED | Email: {email} | IP: {client_ip} | "
                    f"Endpoint: {endpoint} | ExpiredAt: {datetime.fromtimestamp(exp)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )

            if user_role is None:
                auth_middleware_logger.warning(
                    f"TOKEN_NO_ROLE | Email: {email} | IP: {client_ip} | Endpoint: {endpoint}"
                )
                raise credentials_exception

            if user_role not in allowed_roles:
                auth_middleware_logger.warning(
                    f"ROLE_FORBIDDEN | Email: {email} | UserRole: {user_role} | "
                    f"RequiredRoles: {allowed_roles} | IP: {client_ip} | Endpoint: {endpoint}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to perform this action"
                )

            auth_middleware_logger.debug(
                f"AUTH_SUCCESS | Email: {email} | Role: {user_role} | "
                f"UserID: {logged_user_id} | IP: {client_ip} | Endpoint: {endpoint}"
            )

            return logged_user_id

        except HTTPException as he:
            auth_middleware_logger.warning(
                f"AUTH_HTTP_ERROR | Status: {he.status_code} | "
                f"Detail: {he.detail} | IP: {client_ip} | Endpoint: {endpoint}"
            )
            raise he

        except JWTError as je:
            auth_middleware_logger.warning(
                f"JWT_ERROR | Error: {str(je)} | IP: {client_ip} | "
                f"Endpoint: {endpoint} | TokenPrefix: {token[:20]}..."
            )
            raise credentials_exception

        except Exception as e:
            auth_middleware_logger.error(
                f"AUTH_UNEXPECTED_ERROR | Error: {str(e)} | "
                f"IP: {client_ip} | Endpoint: {endpoint}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )

    return role_checker


async def get_current_user(request: Request) -> dict:
    """Get current user from JWT token"""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided"
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def log_suspicious_activity(request: Request, reason: str, details: str = ""):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    endpoint = f"{request.method} {request.url.path}"

    auth_middleware_logger.warning(
        f"SUSPICIOUS_ACTIVITY | Reason: {reason} | "
        f"Endpoint: {endpoint} | IP: {client_ip} | "
        f"UserAgent: {user_agent[:100]} | Details: {details}"
    )


def security_audit(func):
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request:
            client_ip = request.client.host if request.client else "unknown"
            endpoint = f"{request.method} {request.url.path}"
            auth_middleware_logger.info(f"SECURITY_AUDIT | Accessing: {endpoint} | IP: {client_ip}")

        try:
            result = await func(*args, **kwargs)
            if request:
                auth_middleware_logger.info(f"SECURITY_AUDIT_SUCCESS | {endpoint} | IP: {client_ip}")
            return result
        except Exception as e:
            if request:
                auth_middleware_logger.error(
                    f"SECURITY_AUDIT_ERROR | {endpoint} | IP: {client_ip} | Error: {str(e)}"
                )
            raise

    return wrapper