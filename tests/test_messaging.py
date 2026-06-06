from __future__ import annotations

from unittest.mock import Mock, patch

import pika
import pytest

from auth_service.errors import MessagingError
from auth_service.messaging import RabbitSmsPublisher, SmsMessage


def test_publish_declares_durable_queue_and_persistent_message(settings) -> None:
    channel = Mock()
    connection = Mock()
    connection.channel.return_value = channel

    with patch("auth_service.messaging.pika.BlockingConnection", return_value=connection):
        RabbitSmsPublisher(settings).publish(SmsMessage(phone="+989123456789", text="code 123456"))

    channel.queue_declare.assert_called_once_with(queue=settings.sms_queue, durable=True)
    assert channel.basic_publish.call_args.kwargs["routing_key"] == settings.sms_queue
    assert channel.basic_publish.call_args.kwargs["properties"].delivery_mode == 2
    connection.close.assert_called_once()


def test_publish_wraps_rabbitmq_errors(settings) -> None:
    with patch("auth_service.messaging.pika.BlockingConnection", side_effect=pika.exceptions.AMQPConnectionError()):
        with pytest.raises(MessagingError):
            RabbitSmsPublisher(settings).publish(SmsMessage(phone="+989123456789", text="code 123456"))

