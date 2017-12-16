.. This file is a part of the AnyBlok / Dramatiq project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

MEMENTO
=======

How to use dramatiq and which context
-------------------------------------

The goal of dramatiq is to process some task on another system process. 
If your tasks will be done on the same process, you read the wrong soluce.
But if your tasks can be execute in another process, and its take time to process them, your are welcome

The first thing to known is you will need to run to application:

* anyblok_dramatiq: to process the task.
* Another anyblok script to execute the main process, anyblok_pyramid if you have a web service.

Make attention that the both use the same broker, else they should not be communicate each other.

.. warning:: 

    the blok ``dramatiq`` must be installed

To execute your task by dramatiq, you have to define **actor** or **actor_send** on your AnyBlok Model. 
Read the doc of the doc of ``dramatiq`` blok to know how declare it.


Add middleware on dramatiq
--------------------------

**dramatiq** allow to add middleware to improve the process, **anyblok_dramatiq** add one middleware for historize the messages and their status.

You can add in your project an existing **dramatiq** middleware or your own. `read more <https://dramatiq.io/reference.html#middleware>`_ to known existing middleware or how create your own.

**anyblok_dramatiq** add this own console script to run the workers, you need add the middleware in the entrypoint ``anyblok_dramatiq.middleware``::

    setup(
        ...
        entry_points={
            'anyblok_dramatiq.middleware': [
                'mymiddleware=module.path:ClassName',
            ],
        },
        ...
    )

