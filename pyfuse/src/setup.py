# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

from fuse import __version__

setup(name='PyFUSE',
      version=__version__,
      description='a ctypes wrapper around fuse for python 3',
      long_description=('PyFUSE is a ctypes wrapper around fuse written for Python 3.'
                        'I wrote this because all fuse wrappers I found did not work as'
                        'expected with Python 3.'),
      author='Maximilian Köhl',
      author_email='linuxmaxi@googlemail.com',
      url='http://www.github.com/koehlma/pyfuse',
      license='GPLv3',
      packages=['fuse'])
