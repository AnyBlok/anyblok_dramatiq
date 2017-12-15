# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok


class TestBlok2(Blok):

    version = '0.1.0'
    required = ['dramatiq-task']

    @classmethod
    def import_declaration_module(cls):
        from . import model # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import model # noqa
        reload(model)

    def update(self, latest_version):
        self.add_case_simple()
        self.add_case_by_step()
        self.add_case_by_step_without_sub_job()
        self.add_case_parallel()
        self.add_case_parallel_without_sub_job()

    def add_case_simple(self):
        self.registry.Dramatiq.Task.CallMethod.insert(
            label="task1", model="Model.Test",
            method="add_instance")

    def add_case_by_step(self):
        main_task = self.registry.Dramatiq.Task.StepByStep.insert(
            label="task2")
        self.registry.Dramatiq.Task.CallMethod.insert(
            label="subtask1", model="Model.Test",
            method="add_instance", main_task=main_task)
        self.registry.Dramatiq.Task.CallMethod.insert(
            label="subtask2", model="Model.Test",
            method="add_instance", main_task=main_task)

    def add_case_by_step_without_sub_job(self):
        self.registry.Dramatiq.Task.StepByStep.insert(
            label="task3")

    def add_case_parallel(self):
        main_task = self.registry.Dramatiq.Task.Parallel.insert(
            label="task4")
        self.registry.Dramatiq.Task.CallMethod.insert(
            label="subtask1", model="Model.Test",
            method="add_instance", main_task=main_task)
        self.registry.Dramatiq.Task.CallMethod.insert(
            label="subtask2", model="Model.Test",
            method="add_instance", main_task=main_task)

    def add_case_parallel_without_sub_job(self):
        self.registry.Dramatiq.Task.Parallel.insert(
            label="task5")
