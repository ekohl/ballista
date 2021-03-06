# Copyright (c) 2016 the Ballista Project https://gitlab.com/parapet/ballista
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import cmd
from katlibs.modules import promote_cv
import shlex
import sys
from katlibs.main.katello_helpers import get_components
from pprint import pprint
import logging

logging.basicConfig(level=logging.WARNING)


def add_to_subparsers(subparsers):
    parser_cleanout_view = subparsers.add_parser('repl', help='Start repl-shell')
    parser_cleanout_view.set_defaults(funcname='repl')


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class Katloop(cmd.Cmd):
    def __init__(self, connection):
        cmd.Cmd.__init__(self)
        self.connection = connection

    def emptyline(self):
        return

    def do_promote(self, line):

        splitted_options = shlex.split(line)
        if '/' in splitted_options[0]:
            cview_name, version = splitted_options[0].split('/')
        else:
            cview_name = splitted_options[0]
            version = 0

        environment = splitted_options[1]

        promote_cv.promote_cv(self.connection, cvname=cview_name, environment=environment, version=version)

    def help_promote(self):
        print "Promote a content view to a givent environment. Optionally you can specify a version."
        print "Promote newest version:"
        print "   promote <content view name> <environment>"
        print "promote specific version:"
        print "   promote <content view name>/<version> <environment>"

    def do_list_cviews(self, line):
        splitted_options = shlex.split(line)
        if '-j' in splitted_options:
            pprint(self.connection.content_views)
            return
        for cview in self.connection.content_views:
            cview_name = cview['name']
            print cview_name
            try:
                versions = get_components(self.connection.content_views, ('name', cview_name))['versions']
            except KeyError:
                # We do not yet have a published version
                continue
            if '-v' in splitted_options:
                for version in versions:
                    print '    Version: {} ({})'.format(version['version'], version['published'])

    def help_list_cviews(self):
        print "Print content views." \
              "Pass -j to list them in all their json glory, -v to list the versions of the views as well"

    def postloop(self):
        print

    def do_exit(self, line):
        sys.exit()

    def help_exit(self):
        print "Exit the repl"

    def do_EOF(self, line):
        sys.exit()


def main(**kwargs):
    loop = Katloop(kwargs['connection'])
    try:
        loop.cmdloop()
    except KeyboardInterrupt:
        sys.exit()
