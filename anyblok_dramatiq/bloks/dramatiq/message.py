# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, UUID, Selection, DateTime, Json, Text
from anyblok.relationship import Many2One
from datetime import datetime
from dramatiq import Message as DramatiqMessage, get_broker, Actor
from simplejson import loads
from logging import getLogger

logger = getLogger(__name__)


@Declarations.register(Declarations.Model)
class Dramatiq:
    """No SQL Model, use to get tools for dramatiq messaging"""

    @classmethod
    def create_message(cls, actor, *args, **kwargs):
        """Prepare a message and add an entry in the Message Model
        :param actor: an Actor instance
        :param delay: use for postcommit hook send2broker
        :param _*args: args of the actor
        :param _*_*kwargs: kwargs of the actor
        :rtype: dramatiq message instance
        """
        delay = kwargs.pop('delay', None)
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
            message=loads(message.encode())
        )
        cls.postcommit_hook('send2broker', message, delay=delay)
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


@Declarations.register(Declarations.Mixin)
class DramatiqMessageStatus:

    STATUS_NEW = "new"
    STATUS_ENQUEUED = "enqueued"
    STATUS_DELAYED = "delayed"
    STATUS_RUNNING = "running"
    STATUS_FAILED = "failed"
    STATUS_DONE = "done"
    STATUS_SKIPED = "skiped"

    STATUSES = [
        (STATUS_NEW, "New"),
        (STATUS_ENQUEUED, "Enqueued"),
        (STATUS_DELAYED, "Delayed"),
        (STATUS_RUNNING, "Running"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
        (STATUS_SKIPED, "Skiped"),
    ]

    status = Selection(
        selections=STATUSES, default=STATUS_NEW, nullable=False
    )
    created_at = DateTime(nullable=False, default=datetime.now)


@Declarations.register(Declarations.Model.Dramatiq)
class Message(Declarations.Mixin.DramatiqMessageStatus):

    id = UUID(primary_key=True, nullable=False)
    updated_at = DateTime()
    message = Json(nullable=False)

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.update_status(self.status)

    def __str__(self):
        return '<Message (id={self.id}, status={self.status.label})>'.format(
            self=self)

    @classmethod
    def get_instance_of(cls, message):
        return cls.query().filter(cls.id == message.message_id).one_or_none()

    def update_status(self, status, error=None):
        logger.info("Update message %s status => %s",
                    self, dict(self.STATUSES).get(status))
        self.status = status
        self.updated_at = datetime.now()
        self.registry.Dramatiq.Message.History.insert(
            status=status, created_at=self.updated_at, message=self,
            error=error
        )


@Declarations.register(Declarations.Model.Dramatiq.Message)
class History(Declarations.Mixin.DramatiqMessageStatus):

    id = Integer(primary_key=True)
    message = Many2One(model=Declarations.Model.Dramatiq.Message,
                       one2many="histories", nullable=False,
                       foreign_key_options={'ondelete': 'cascade'})
    error = Text()
