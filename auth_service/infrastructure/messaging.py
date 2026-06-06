from __future__ import annotations

import json
from typing import Callable

import pika
from pika.exceptions import AMQPError, UnroutableError

from auth_service.config import Settings
from auth_service.errors import MessagingError
from auth_service.application.ports import SmsMessage


class RabbitSmsPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publish(self, message: SmsMessage) -> None:
        try:
            params = pika.URLParameters(self.settings.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            try:
                channel = connection.channel()
                channel.queue_declare(queue=self.settings.sms_queue, durable=True)
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange="",
                    routing_key=self.settings.sms_queue,
                    body=json.dumps(message.__dict__).encode(),
                    mandatory=True,
                    properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
                )
            finally:
                connection.close()
        except (AMQPError, UnroutableError) as exc:
            raise MessagingError("failed to publish sms message") from exc


class RabbitSmsConsumer:
    def __init__(self, settings: Settings, handler: Callable[[SmsMessage], None]) -> None:
        self.settings = settings
        self.handler = handler

    def start(self) -> None:
        try:
            params = pika.URLParameters(self.settings.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=self.settings.sms_queue, durable=True)
            channel.basic_qos(prefetch_count=10)
        except AMQPError as exc:
            raise MessagingError("failed to start sms consumer") from exc

        def callback(ch, method, _properties, body: bytes) -> None:
            try:
                payload = json.loads(body.decode())
                if not isinstance(payload.get("phone"), str) or not isinstance(payload.get("text"), str):
                    raise ValueError("invalid sms payload")
                self.handler(SmsMessage(phone=payload["phone"], text=payload["text"]))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        try:
            channel.basic_consume(queue=self.settings.sms_queue, on_message_callback=callback)
            channel.start_consuming()
        except AMQPError as exc:
            raise MessagingError("sms consumer stopped unexpectedly") from exc
        finally:
            if connection.is_open:
                connection.close()
