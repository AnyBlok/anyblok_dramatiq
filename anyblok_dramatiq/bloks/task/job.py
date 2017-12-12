# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import UUID, Selection, DateTime, Json, Text
from anyblok.relationship import Many2One
from datetime import datetime
from uuid import uuid1
from anyblok_dramatiq import actor_send
from logging import getLogger

logger = getLogger(__name__)


@Declarations.register(Declarations.Model.Dramatiq)
class Job:
    STATUS_NEW = "new"
    STATUS_WAITING = "waiting"
    STATUS_RUNNING = "running"
    STATUS_FAILED = "failed"
    STATUS_DONE = "done"

    STATUSES = [
        (STATUS_NEW, "New"),
        (STATUS_WAITING, "Waiting"),
        (STATUS_RUNNING, "Running"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
    ]

    uuid = UUID(primary_key=True, nullable=False, default=uuid1, binary=False)
    create_at = DateTime(default=datetime.now, nullable=False)
    update_at = DateTime(default=datetime.now, nullable=False,
                         auto_update=True)
    run_at = DateTime()
    data = Json(nullable=False)
    status = Selection(
        selections=STATUSES, default=STATUS_NEW, nullable=False
    )
    task = Many2One(model=Declarations.Model.Dramatiq.Task, nullable=False)
    main_job = Many2One(model='Model.Dramatiq.Job', one2many="sub_jobs")
    error = Text()

    @actor_send()
    def run(cls, job_uuid=None, autocommit=True):
        try:
            job = cls.query().filter(cls.uuid == job_uuid).one()
            job.status = cls.STATUS_RUNNING
            if autocommit:
                cls.registry.commit()  # use to save the state

            job.task.run(job)
            job.status = cls.STATUS_DONE
            if autocommit:
                cls.registry.commit()  # use to save the state
        except Exception as e:
            logger.error(str(e))
            cls.registry.rollback()
            job.status = cls.STATUS_FAILED
            job.error = str(e)

            if autocommit:
                cls.registry.commit()  # use to save the state

    def call_main_job(self):
        if self.main_job:
            self.main_job.lock()
            self.main_job.run_next()
