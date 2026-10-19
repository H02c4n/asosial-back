import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token: str):
    try:
        access = AccessToken(token)
        user_id = access['user_id']
        logger.info(f"[WS] JWT OK, user_id={user_id}")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        logger.info(f"[WS] Kullanıcı bulundu: {user.username}")
        return user
    except Exception as e:
        logger.error(f"[WS] JWT HATASI: {type(e).__name__}: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        if token:
            logger.info(f"[WS] Bağlantı geldi, token={token[:30]}...")
            scope['user'] = await get_user_from_token(token)
        else:
            logger.warning("[WS] Token yok")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)