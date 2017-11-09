# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String


@Declarations.register(Declarations.Model)
class Task():
    id = Integer(primary_key=True)
    name = String(nullable=False)

    @classmethod
    def add(cls, name):
        cls.insert(name=name)
