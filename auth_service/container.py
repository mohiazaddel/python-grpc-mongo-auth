from __future__ import annotations

from dependency_injector import containers, providers

from .config import load_settings
from .database import MongoStore
from .grpc_service import AuthService
from .kavenegar import KavenegarClient
from .messaging import RabbitSmsConsumer, RabbitSmsPublisher
from .repositories import OtpRepository, RefreshTokenRepository, UserRepository
from .security import OtpService, TokenService
from .services import AuthApplicationService


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(load_settings)

    store = providers.Singleton(MongoStore, settings=settings)

    users = providers.Factory(UserRepository, store=store)
    otps = providers.Factory(OtpRepository, store=store)
    refresh_tokens = providers.Factory(RefreshTokenRepository, store=store)

    otp_service = providers.Factory(OtpService, otps=otps, settings=settings)
    token_service = providers.Factory(
        TokenService,
        users=users,
        refresh_tokens=refresh_tokens,
        settings=settings,
    )
    sms_publisher = providers.Factory(RabbitSmsPublisher, settings=settings)
    auth_app = providers.Factory(
        AuthApplicationService,
        settings=settings,
        users=users,
        otp_service=otp_service,
        token_service=token_service,
        sms_publisher=sms_publisher,
    )

    grpc_auth_service = providers.Factory(AuthService, auth_service=auth_app)

    kavenegar_client = providers.Factory(KavenegarClient, settings=settings)
    sms_consumer = providers.Factory(
        RabbitSmsConsumer,
        settings=settings,
        handler=kavenegar_client.provided.send_sms,
    )
