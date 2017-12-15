# This file is a part of the AnyBlok / Dramatiq api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok, BlokManager
from anyblok_dramatiq.release import version


class DramatiqBlok(Blok):
    """Dramatiq's Blok class definition
    """
    version = version
    author = "jssuzanne"
    required = ['anyblok-core']

    @classmethod
    def import_declaration_module(cls):
        """Python module to import in the given order at start-up
        """
        from . import message  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        """Python module to import while reloading server (ie when
        adding Blok at runtime
        """
        from . import message  # noqa
        reload(message)

    @classmethod
    def declare_actors(cls, registry):
        """Actor declaration

        ::

            from anyblok_dramatiq import (
                declare_actor_for,
                declare_actor_send_for,
            )
            declare_actor_for(Model.methode_name)
            # or
            declare_actor_send_for(Model.methode_name)
        """

    def load(self):
        """Load all the actor defined in all the installed bloks"""
        Blok = self.registry.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            if hasattr(b, 'declare_actors'):
                b.declare_actors(self.registry)
