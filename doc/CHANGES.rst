.. This file is a part of the AnyBlok / Dramatiq project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

CHANGELOG
=========

1.0.3 (2018-02-24)
------------------

* [REF] Anyblok 0.17.0 changed setter to add application and application 
  groups, So I had to adapt the existing to use new setter

1.0.2 (2018-02-12)
------------------

* [FIX] multi process lock
  AnyBlok seem lock the data base during the migration, the dramatiq process
  don't migrate the data base, the migration is now forbidden

1.0.1 (2018-01-10)
------------------

* [FIX] put the configuration ``dramatiq-broker`` on the default application

1.0.0 (2017-12-23)
------------------

* [IMP] dramatiq console script to execute workers process
* [IMP] actor and actor_send decorator to define dramatiq actor
* [IMP] dramatiq middleware to modify ``Model.Dramatiq.Message`` status
* [IMP] dramatiq blok to historize the message and status
* [IMP] dramatiq-task to add a back task with dramatiq
