# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String, Selection, DateTime
from anyblok.relationship import Many2One
from datetime import datetime
from logging import getLogger

logger = getLogger(__name__)
Model = Declarations.Model


@Declarations.register(Model.Dramatiq)
class Task:
    """Main Task, define the main table"""
    TASK_TYPE = None

    id = Integer(primary_key=True)
    label = String(nullable=False)
    create_at = DateTime(default=datetime.now, nullable=False)
    update_at = DateTime(default=datetime.now, nullable=False, auto_update=True)
    task_type = Selection(selections="get_task_type", nullable=False)
    order = Integer(nullable=False, default=100)
    main_task = Many2One(model='Model.Dramatiq.Task',
                         one2many="sub_tasks")

    @classmethod
    def get_task_type(cls):
        """List the task type possible"""
        return {
            'call_method': 'Call classmethod',
            'stepbystep': 'Step by Step',
            'parallel': 'Parallel steps',
        }

    @classmethod
    def define_mapper_args(cls):
        """Polymorphism configuration"""
        mapper_args = super(Task, cls).define_mapper_args()
        if cls.__registry_name__ == Model.Dramatiq.Task.__registry_name__:
            mapper_args.update({
                'polymorphic_identity': cls.TASK_TYPE,
                'polymorphic_on': cls.task_type,
            })
        else:
            mapper_args.update({
                'polymorphic_identity': cls.TASK_TYPE,
            })

        return mapper_args

    def do_the_job(self, main_job=None, run_at=None, with_args=None,
                   with_kwargs=None):
        """Create a job for this tash and add send it to dramatiq

        :param main_job: parent job if exist
        :param run_at: datetime to execute the job
        :param with_args: tuple of the argument to pass at the job
        :param with_kwargs: dict of the argument to pass at the job
        """
        values = dict(
            run_at=run_at,
            data=dict(
                with_args=with_args or tuple(),
                with_kwargs=with_kwargs or dict()
            ),
            task=self,
            main_job=main_job
        )
        job = self.registry.Dramatiq.Job.insert(**values)
        # FIXME dramatiq don t accept uuid, waiting the next version
        self.registry.Dramatiq.Job.run(
            job_uuid=str(job.uuid), run_at=run_at)

    def run(self, job):
        """Execute the task for one job

        :param job: job executed
        """
        raise Exception("No task definition for job %r" % job)

    def run_next(self, job):
        """next action to execute when a sub job finish this task for one job

        :param job: job executed
        """
        raise Exception("No next action define for this task for job %r" % job)


@Declarations.register(Model.Dramatiq.Task)
class CallMethod(Model.Dramatiq.Task):
    """Task type which call a classmethod on a model"""
    TASK_TYPE = 'call_method'

    id = Integer(
        primary_key=True,
        foreign_key=Model.Dramatiq.Task.use('id').options(
            ondelete='cascade'))
    model = String(foreign_key=Model.System.Model.use('name'), nullable=False)
    method = String(nullable=False)

    def run(self, job):
        """Execute the task for one job

        Execute the classmethod define by the entry model and method on the
        instance

        :param job: job executed
        """
        logger.info('Run the task %r for job %r' % (self, job))
        Model = self.registry.get(self.model)
        method = self.method
        data_args = job.data.get('with_args', tuple())
        data_kwargs = job.data.get('with_kwargs', dict())
        getattr(Model, method)(job.uuid, *data_args, **data_kwargs)
        job.status = self.registry.Dramatiq.Job.STATUS_DONE
        job.call_main_job()


@Declarations.register(Model.Dramatiq.Task)
class StepByStep(Model.Dramatiq.Task):
    """Call each sub job one after one"""
    TASK_TYPE = 'stepbystep'

    def run(self, job):
        """Execute the task for one job

        Define all sub job and call the run_next method

        :param job: job executed
        """
        logger.info('Run the sub_job for job %r' % job)
        for task in job.task.sub_tasks:
            values = dict(
                data=job.data,
                task=task,
                main_job=job
            )
            self.registry.Dramatiq.Job.insert(**values)

        job.status = self.registry.Dramatiq.Job.STATUS_WAITING
        self.run_next(job)

    def run_next(self, job):
        """next action to execute when a sub job finish this task for one job

        Run the next sub job if all the sub job have not been executing
        else change the status of the job

        :param job: job executed
        """
        Job = self.registry.Dramatiq.Job
        query = Job.query().filter(Job.main_job == job)
        query = query.filter(Job.status == Job.STATUS_NEW)
        query = query.join(Job.task).order_by(self.__class__.order)
        if query.count():
            sub_job = query.first()
            # FIXME dramatiq don t accept uuid, waiting the next version
            self.registry.Dramatiq.Job.run(job_uuid=str(sub_job.uuid))
        else:
            job.status = self.registry.Dramatiq.Job.STATUS_DONE
            job.call_main_job()


@Declarations.register(Model.Dramatiq.Task)
class Parallel(Model.Dramatiq.Task):
    """Call each sub job"""
    TASK_TYPE = 'parallel'

    def run(self, job):
        """Execute the task for one job

        Define all sub job and send them to dramatiq actor

        :param job: job executed
        """
        logger.info('Run the sub_job for job %r' % job)
        job.status = self.registry.Dramatiq.Job.STATUS_WAITING
        for task in job.task.sub_tasks:
            values = dict(
                data=job.data,
                task=task,
                main_job=job,
            )
            sub_job = self.registry.Dramatiq.Job.insert(**values)
            self.registry.Dramatiq.Job.run(job_uuid=str(sub_job.uuid))
        else:
            self.run_next(job)

    def run_next(self, job):
        """next action to execute when a sub job finish this task for one job

        Change the status of the job if all sub job are done

        :param job: job executed
        """
        # the lock is already done by call_main_job
        Job = self.registry.Dramatiq.Job
        query = Job.query().filter(Job.main_job == job)
        query = query.filter(Job.status == Job.STATUS_NEW)
        if not query.count():
            job.status = self.registry.Dramatiq.Job.STATUS_DONE
            job.call_main_job()
