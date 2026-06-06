from __future__ import annotations

from typing import Type, TypeVar, Union

from injector import Injector, Scope, ScopeDecorator

from auth_service.container import AppModule

T = TypeVar("T")


class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Injection(metaclass=Singleton):
    def __init__(self) -> None:
        self._injector: Injector = Injector([AppModule()])
        self._inited = False

    def injector(self) -> Injector:
        if not self._inited:
            self._inited = True
        return self._injector

    def get(self, interface: Type[T], scope: Union[ScopeDecorator, Type[Scope], None] = None) -> T:
        return self.injector().get(interface, scope)

