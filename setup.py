"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

setup.py: head file for installation

Organdiae is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version
3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301
USA
"""


from distutils.core import setup

setup(name='Organdiae',
      version='0.0.2',
      description='Interactive mind-mapping for pre-composition',
      author='Mike Solomon',
      author_email='organdiae@organdiae.com',
      url='http://www.organdiae.com/',
      packages=['organdiae','organdiae.core','organdiae.addons'],
)
                                         