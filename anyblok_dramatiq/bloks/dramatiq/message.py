# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import UUID, Selection, DateTime, Json
from datetime import datetime
from dramatiq import Message as DramatiqMessage, get_broker, Actor
import json
from logging import getLogger

logger = getLogger(__name__)


@Declarations.register(Declarations.Model)
class Dramatiq():
    """No SQL Model, use to get tools for dramatiq messaging"""

    @classmethod
    def create_message(cls, actor, *args, **kwargs):
        """Prepare a message and add an entry in the Message Model
        :param actor: an Actor instance
        :param _*args: args of the actor
        :param _*_*kwargs: kwargs of the actor
        :rtype: dramatiq message instance
        """
        if not isinstance(actor, Actor):
            logger.warning(
                "[create_message] can't work without an actor"
            )
            return None

        message = DramatiqMessage(
            queue_name=actor.queue_name,
            actor_name=actor.actor_name,
            args=args,  kwargs=kwargs,
            options=dict()
        )
        message.broker = actor.broker
        cls.Message.insert(
            id=message.message_id,
            message=json.loads(message.encode())
        )
        return message

    @classmethod
    def send2broker(cls, *messages, delay=None):
        """Send all the messages with the delay

        :param _*messages: message instance list
        :param delay: delay before send
        """
        for message in messages:
            broker = message.broker or get_broker()
            broker.enqueue(message, delay=delay)


@Declarations.register(Declarations.Model.Dramatiq)
class Message():

    STATUS_NEW = "new"
    STATUS_ENQUEUED = "enqueued"
    STATUS_DELAYED = "delayed"
    STATUS_RUNNING = "running"
    STATUS_FAILED = "failed"
    STATUS_DONE = "done"

    STATUSES = [
        (STATUS_NEW, "New"),
        (STATUS_ENQUEUED, "Enqueued"),
        (STATUS_DELAYED, "Delayed"),
        (STATUS_RUNNING, "Running"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
    ]

    id = UUID(primary_key=True, nullable=False)
    status = Selection(selections=STATUSES, default=STATUS_NEW)
    created_at = DateTime(nullable=False, default=datetime.now)
    updated_at = DateTime(nullable=False, default=datetime.now)
    message = Json(nullable=False)

    @classmethod
    def get_instance_of(cls, message):
        return cls.query().filter(cls.id == message.message_id).one_or_none()
