
from dataclasses import dataclass
import os

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
import httpx
from jose import JWTError
import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import ImmatureSignatureError, InvalidSignatureError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.db.database import get_db_session

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')

ALGORITHMS = ['RS256']

bearer_scheme = HTTPBearer()


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
# ) -> dict:
#     token = credentials.credentials
#     try:
#         if not token:
#             raise HTTPException(
#                 status_code=401,
#                 detail='No autorizado o token no encontrado en el encabezado.',
#             )

#         user = verify_jwt(token, AUTH0_DOMAIN, verify_iat=False)
#         return user
#     except JWTError:
#         raise HTTPException(status_code=401, detail='Token inválido o expirado')
def get_current_user(
    token: str = Query(...),  # Ahora tomamos el token del parámetro de consulta
) -> dict:
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail='No autorizado o token no encontrado en el parámetro de consulta.',
            )

        # Verificamos el token utilizando la lógica de verificación
        user = verify_jwt(token, AUTH0_DOMAIN, verify_iat=False)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido o expirado')

def get_rsa_key(token: str, AUTH0_DOMAIN: str) -> dict:
    '''Obtain the RSA key from Auth0 JWKS uri based on the token's kid.'''
    headers = jwt.get_unverified_header(token)
    kid = headers['kid']
    jwks_uri = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
    jwks_client = httpx.Client()
    response = jwks_client.get(jwks_uri)
    keys = response.json()['keys']
    for key in keys:
        if key['kid'] == kid:
            return {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            }
    return None


def verify_jwt(token: str, AUTH0_DOMAIN: str, verify_iat: bool = True):
    try:

        rsa_key = get_rsa_key(token, AUTH0_DOMAIN)
        if rsa_key is None:
            raise HTTPException(
                status_code=401,
                detail='No se pudo encontrar la clave pública adecuada.',
            )

        public_key = RSAAlgorithm.from_jwk(rsa_key)

        options = {'verify_iat': verify_iat}  # Ajusta las opciones de verificación

        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=AUTH0_AUDIENCE,
            issuer=f'https://{AUTH0_DOMAIN}/',
            options=options,  # Añade las opciones de verificación
        )
        return payload
    except ImmatureSignatureError:
        return JSONResponse(
            status_code=401, content={'detail': 'Token no válido aún (iat)'}
        )
    except InvalidSignatureError:
        return JSONResponse(
            status_code=401, content={'detail': 'Firma del token inválida'}
        )
    except JWTError:
        return JSONResponse(
            status_code=401, content={'detail': 'Token inválido o expirado'}
        )


async def get_session_token(request: Request):
    authorization: str = request.headers.get('Authorization')
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail='No autorizado o token no encontrado en el encabezado',
        )
    return authorization.split('Bearer ')[1]  # Devolver el token


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail='No autorizado o token no encontrado en el encabezado',
        )

    user = verify_jwt(credentials.credentials, AUTH0_DOMAIN)
    if not user:
        raise HTTPException(status_code=401, detail='Token inválido o expirado')

    return JSONResponse({'message': 'Usuario autenticado con éxito', 'user': user})


@dataclass
class JsonWebToken:
    '''Perform JSON Web Token (JWT) validation using PyJWT'''

    jwt_access_token: str
    auth0_issuer_url: str = AUTH0_DOMAIN
    auth0_audience: str = AUTH0_AUDIENCE
    algorithm: str = 'RS256'
    jwks_uri: str = f'https://{auth0_issuer_url}/.well-known/jwks.json'

    def validate(self):
        try:
            rsa_key = get_rsa_key(self.jwt_access_token, self.auth0_issuer_url)
            if rsa_key is None:
                raise UnableCredentialsException

            public_key = RSAAlgorithm.from_jwk(rsa_key)
            payload = jwt.decode(
                self.jwt_access_token,
                public_key,
                algorithms=self.algorithm,
                audience=self.auth0_audience,
                issuer=f'https://{self.auth0_issuer_url}/',
            )
        except jwt.exceptions.PyJWKClientError:
            raise UnableCredentialsException
        except jwt.exceptions.InvalidTokenError:
            raise BadCredentialsException
        return payload


def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return JsonWebToken(credentials.credentials).validate()


class PermissionsValidator:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, token: str = Depends(validate_token)):
        token_permissions = token.get('permissions')
        token_permissions_set = set(token_permissions)
        required_permissions_set = set(self.required_permissions)

        if not required_permissions_set.issubset(token_permissions_set):
            raise PermissionDeniedException

# class AuthenticationChecker:
#     async def __call__(self, request: Request):
#         try:
#             token = await get_session_token(request)
#             if not token:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail='No autorizado o token no encontrado en el encabezado.',
#                 )

#             # Verificamos el token utilizando la lógica de verificación
#             user = verify_jwt(token, AUTH0_DOMAIN)
#             return user
#         except JWTError:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail='Token inválido o expirado.',
#             )
#         except InvalidSignatureError:
#             raise BadCredentialsException()


class AuthenticationChecker:
    async def __call__(self, request: Request, token: str = Query(None)):
        try:
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail='Token no encontrado en el parámetro de consulta.',
                )
            # Verificamos el token utilizando la lógica de verificación
            user = verify_jwt(token, AUTH0_DOMAIN)
            return user
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail='Token inválido o expirado.',
            )
        except InvalidSignatureError:
            raise HTTPException(
                status_code=401,
                detail='Firma del token inválida.',
            )


class BadCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Bad credentials'
        )


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied'
        )


class RequiresAuthenticationException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Requires authentication'
        )


class UnableCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to verify credentials',
        )


def get_optional_field(
    field_name: str,
    request: Request,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> str | None:
    if os.getenv('TESTING'):
        return request.json().get(field_name)
    else:
        return current_user.get(field_name)


def get_user_id(
    user_id: str | None = Depends(
        lambda request, db, current_user: get_optional_field(
            'user_id', request, db, current_user
        )
    ),
) -> str:
    if not user_id:
        raise HTTPException(status_code=506, detail='Missing required field: user_id')
    return user_id
