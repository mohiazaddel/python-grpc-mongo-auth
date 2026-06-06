from __future__ import annotations

from injector import Module, provider, singleton

from .application.auth import AuthApplicationService
from .config import Settings, load_settings
from .domain.auth import OtpService, TokenService
from .infrastructure.database import MongoStore
from .infrastructure.kavenegar import KavenegarClient
from .infrastructure.messaging import RabbitSmsConsumer, RabbitSmsPublisher
from .infrastructure.repositories import OtpRepository, RefreshTokenRepository, UserRepository
from .interfaces.grpc.service import AuthGrpcService


class AppModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return load_settings()

    @singleton
    @provider
    def provide_store(self, settings: Settings) -> MongoStore:
        return MongoStore(settings)

    @provider
    def provide_users(self, store: MongoStore) -> UserRepository:
        return UserRepository(store)

    @provider
    def provide_otps(self, store: MongoStore) -> OtpRepository:
        return OtpRepository(store)

    @provider
    def provide_refresh_tokens(self, store: MongoStore) -> RefreshTokenRepository:
        return RefreshTokenRepository(store)

    @provider
    def provide_otp_service(self, otps: OtpRepository, settings: Settings) -> OtpService:
        return OtpService(otps, settings)

    @provider
    def provide_token_service(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        settings: Settings,
    ) -> TokenService:
        return TokenService(users, refresh_tokens, settings)

    @provider
    def provide_sms_publisher(self, settings: Settings) -> RabbitSmsPublisher:
        return RabbitSmsPublisher(settings)

    @provider
    def provide_auth_application_service(
        self,
        settings: Settings,
        users: UserRepository,
        otp_service: OtpService,
        token_service: TokenService,
        sms_publisher: RabbitSmsPublisher,
    ) -> AuthApplicationService:
        return AuthApplicationService(settings, users, otp_service, token_service, sms_publisher)

    @provider
    def provide_grpc_auth_service(self, auth_service: AuthApplicationService) -> AuthGrpcService:
        return AuthGrpcService(auth_service)

    @provider
    def provide_kavenegar_client(self, settings: Settings) -> KavenegarClient:
        return KavenegarClient(settings)

    @provider
    def provide_sms_consumer(self, settings: Settings, kavenegar_client: KavenegarClient) -> RabbitSmsConsumer:
        return RabbitSmsConsumer(settings, kavenegar_client.send_sms)
