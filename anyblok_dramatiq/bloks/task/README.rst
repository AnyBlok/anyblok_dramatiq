.. This file is a part of the AnyBlok / Dramatiq project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Memento
~~~~~~~

The tasks is based on dramatiq, The instance of the model:

* Task: define what the task have to do
* Job: historize the execution of an instance of Task with specific data

``Model.Dramatiq.Task``
```````````````````````

This model is not directly useable, you have to use polymosphic model:

* ``Model.Dramatiq.Task.CallMethod``: call a classmethod on a model, defined by the task
* ``Model.Dramatiq.Task.StepByStep``: call each sub task one by one on function of the order
* ``Model.Dramatiq.Task.Parallel``: call all sub tasks on one shot

``Model.Dramatiq.Job``
``````````````````````

The job is the execution of the task with dramatiq, The job historize also action done and action to do.
To create a job, you must get a task create the job with the method ``do_the_job``::

    task = registry.Dramatiq.Task.query().first()
    task.do_the_job(with_args=tuple(), with_kwargs=dict(), run_at=a_datetime)
    # this job will not be traited now and by the process but by another process


.. note::

    In the case where the task will be an ``StepByStep`` or ``Parallel`` task, then the 
    task create one or more job, one for the job and one for sub jobs
