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
from anyblok.environment import EnvironmentManager
from datetime import datetime
from uuid import uuid1
from anyblok_dramatiq import actor_send
from time import sleep
from sqlalchemy.exc import OperationalError
from logging import getLogger

logger = getLogger(__name__)


@Declarations.register(Declarations.Model.Dramatiq)
class Job:
    """The job is an execution of an instance of task"""
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
    def run(cls, job_uuid=None):
        """dramatiq actor to execute a specific task"""
        autocommit = EnvironmentManager.get('job_autocommit', True)
        try:
            job = cls.query().filter(cls.uuid == job_uuid).one()
            job.status = cls.STATUS_RUNNING
            if autocommit:
                cls.registry.commit()  # use to save the state

            job.task.run(job)

            if autocommit:
                cls.registry.commit()  # use to save the state
        except Exception as e:
            logger.error(str(e))
            cls.registry.rollback()
            job.status = cls.STATUS_FAILED
            job.error = str(e)

            if autocommit:
                cls.registry.commit()  # use to save the state

            raise e

    def lock(self):
        """lock the job to be sure that only one thread execute the run_next"""
        Job = self.__class__
        while True:
            try:
                Job.query().with_for_update(nowait=True).filter(
                    Job.uuid == self.uuid).one()
                break
            except OperationalError:
                sleep(1)

    def call_main_job(self):
        """Call the main job if exist to do the next action of the main job"""
        if self.main_job:
            self.main_job.lock()
            self.main_job.task.run_next(self.main_job)
