# This file is a part of the AnyBlok / Dramatiq project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import DramatiqDBTestCase
from anyblok.environment import EnvironmentManager
from anyblok_dramatiq import call_directly_the_actor_send


class TestTask(DramatiqDBTestCase):

    blok_entry_points = ('bloks', 'test_bloks')

    def setUp(self):
        super(TestTask, self).setUp()
        self.registry = registry = self.init_registry(None)
        registry.upgrade(install=('test_dramatiq_2',))
        EnvironmentManager.set('job_autocommit', False)

    def test_simple_case(self):
        Job = self.registry.Dramatiq.Job
        Q = Job.query()
        Task = self.registry.Dramatiq.Task
        task = Task.query().filter(Task.label == 'task1').one()
        self.assertFalse(Q.count())
        with call_directly_the_actor_send():
            task.do_the_job(with_args=('test 1',))

        self.assertEqual(Q.count(), 1)
        job = Q.one()
        self.assertEqual(job.status, Job.STATUS_DONE)

    def test_simple_case_2(self):
        Job = self.registry.Dramatiq.Job
        Q = Job.query()
        Task = self.registry.Dramatiq.Task
        task = Task.query().filter(Task.label == 'task1').one()
        self.assertFalse(Q.count())
        task.do_the_job(with_args=('test 1',))
        self.assertEqual(Q.count(), 1)
        job = Q.one()
        self.assertEqual(job.status, Job.STATUS_NEW)
        job.task.run(job)
        self.assertEqual(job.status, Job.STATUS_DONE)

    def test_step_by_step(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Q = Job.query().join(Job.task)
        task = Task.query().filter(Task.label == 'task2').one()
        self.assertFalse(Q.count())
        with call_directly_the_actor_send():
            task.do_the_job(with_args=('test 2',))
        self.assertEqual(Q.count(), 3)
        main_job = Q.filter(Task.label == 'task2').one()
        sub_job1 = Q.filter(Task.label == 'subtask1').one()
        sub_job2 = Q.filter(Task.label == 'subtask2').one()
        self.assertEqual(main_job.status, Job.STATUS_DONE)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_DONE)

    def test_step_by_step_2(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Message = self.registry.Dramatiq.Message
        Q = Job.query().join(Job.task)
        Qm = Message.query()
        task = Task.query().filter(Task.label == 'task2').one()
        self.assertFalse(Q.count())
        task.do_the_job(with_args=('test 2',))
        self.assertEqual(Q.count(), 1)
        self.assertEqual(Qm.count(), 1)
        main_job = Q.filter(Task.label == 'task2').one()
        self.assertEqual(main_job.status, Job.STATUS_NEW)
        main_job.task.run(main_job)
        self.assertEqual(Q.count(), 3)
        self.assertEqual(Qm.count(), 2)
        sub_job1 = Q.filter(Task.label == 'subtask1').one()
        sub_job2 = Q.filter(Task.label == 'subtask2').one()
        self.assertEqual(main_job.status, Job.STATUS_WAITING)
        self.assertEqual(sub_job1.status, Job.STATUS_NEW)
        self.assertEqual(sub_job2.status, Job.STATUS_NEW)
        sub_job1.task.run(sub_job1)
        self.assertEqual(main_job.status, Job.STATUS_WAITING)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_NEW)
        self.assertEqual(Qm.count(), 3)
        sub_job2.task.run(sub_job2)
        self.assertEqual(main_job.status, Job.STATUS_DONE)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_DONE)

    def test_step_by_step_without_sub_job(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Q = Job.query().join(Job.task)
        task = Task.query().filter(Task.label == 'task3').one()
        self.assertFalse(Q.count())
        with call_directly_the_actor_send():
            task.do_the_job(with_args=('test 2',))

        self.assertEqual(Q.count(), 1)
        main_job = Q.filter(Task.label == 'task3').one()
        self.assertEqual(main_job.status, Job.STATUS_DONE)

    def test_parallel(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Q = Job.query().join(Job.task)
        task = Task.query().filter(Task.label == 'task4').one()
        self.assertFalse(Q.count())
        with call_directly_the_actor_send():
            task.do_the_job(with_args=('test 2',))

        self.assertEqual(Q.count(), 3)
        main_job = Q.filter(Task.label == 'task4').one()
        sub_job1 = Q.filter(Task.label == 'subtask1').one()
        sub_job2 = Q.filter(Task.label == 'subtask2').one()
        self.assertEqual(main_job.status, Job.STATUS_DONE)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_DONE)

    def test_parallel_2(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Message = self.registry.Dramatiq.Message
        Q = Job.query().join(Job.task)
        Qm = Message.query()
        task = Task.query().filter(Task.label == 'task4').one()
        self.assertFalse(Q.count())
        task.do_the_job(with_args=('test 2',))
        self.assertEqual(Q.count(), 1)
        self.assertEqual(Qm.count(), 1)
        main_job = Q.filter(Task.label == 'task4').one()
        self.assertEqual(main_job.status, Job.STATUS_NEW)
        main_job.task.run(main_job)
        self.assertEqual(Q.count(), 3)
        self.assertEqual(Qm.count(), 3)
        sub_job1 = Q.filter(Task.label == 'subtask1').one()
        sub_job2 = Q.filter(Task.label == 'subtask2').one()
        self.assertEqual(main_job.status, Job.STATUS_WAITING)
        self.assertEqual(sub_job1.status, Job.STATUS_NEW)
        self.assertEqual(sub_job2.status, Job.STATUS_NEW)
        sub_job1.task.run(sub_job1)
        self.assertEqual(main_job.status, Job.STATUS_WAITING)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_NEW)
        sub_job2.task.run(sub_job2)
        self.assertEqual(main_job.status, Job.STATUS_DONE)
        self.assertEqual(sub_job1.status, Job.STATUS_DONE)
        self.assertEqual(sub_job2.status, Job.STATUS_DONE)

    def test_parallel_without_sub_task(self):
        Job = self.registry.Dramatiq.Job
        Task = self.registry.Dramatiq.Task
        Q = Job.query().join(Job.task)
        task = Task.query().filter(Task.label == 'task5').one()
        self.assertFalse(Q.count())
        with call_directly_the_actor_send():
            task.do_the_job(with_args=('test 2',))
        self.assertEqual(Q.count(), 1)
        main_job = Q.filter(Task.label == 'task5').one()
        self.assertEqual(main_job.status, Job.STATUS_DONE)
