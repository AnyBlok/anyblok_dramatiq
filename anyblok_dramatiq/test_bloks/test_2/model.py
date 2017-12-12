# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String


@Declarations.register(Declarations.Model)
class Test():
    id = Integer(primary_key=True)
    name = String(nullable=False)

    @classmethod
    def add_instance(cls, job_uuid, name):
        cls.insert(name=name)
