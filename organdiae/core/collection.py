"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

collections.py: creates simple collections used by organdiae

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

from core import _OrgandiaeObject, OrgandiaeError

class Collection(_OrgandiaeObject) :
  """
  One of two pre-defined return types for ``CFunction``.  Used with ``Tags`` in the standard bootstrap (``bs``).
  
  .. todo::
    
    Create a ``__mul__`` function that makes Cartesian products of collections.  Mult would be commutative for sets but non-commutative for strings and lists.
  """
  def __init__(self, s=None) :
    """Init function, where s should be a set, list, string, or generally some sort of collection."""
    self.s = s
  def isEmpty(self) :
    """Returns true if self.s is not initialized with some sort of collection."""
    if self.s == None : return True
    return False
  def reset(self) :
    """Resets self.s back to None."""
    self.s = None
  def initialize(self, y) :
    """A delayed init function, used by CFunctions to set self.s."""
    if self.s : return OrgandiaeError("Already initialized...")
    self.s = y.s
  def __add__(self, y) :
    """Defines addition between two collections as their union/concatenation."""
    if type(y) == type(self.s) :
      return Collection(self.s + y)
    return Collection(self.s + y.s)
  def __str__(self) :
    return str(self.s)

class CFunction(_OrgandiaeObject) :
  """
  Every entry in ``edge.f``, where ``edge`` is an instance of ``Edge``, MUST be an instance of ``CFunction`` (or subclassed from ``CFunction``).
  
  Here's how it works (assume that ``cf`` is an instance of ``CFunction``:
  
  * A list of lines of code are in ``cf.fstrings`` that will be Just-In-Time compiled every time a function is called.  The last line of fstrings must be the return value.
  * All predefined arguments to said function are in ``args``.
  * When ``cf`` is called, the arguments with which it is called are post-pended to the above-defined args list.  The function generated from fstrings is evaluated, and the return value is passed out.

  Why so complicated?  Because Python cannot pickle functions, so they need to be JIT compiled.
  
  .. todo::
    
    Make functions JIT compiled once instead of every time ``__call__`` is invoked.  Then, when pickling a CFunction, defined its pickling so that it omits this declaration.
  """
  def __init__(self, fstrings, args) :
    """Init function, taking `fstrings` and `args` as defined in the docstring for ``CFunction``."""
    self.fstrings = fstrings
    self.args = args
  def __call__(self, *inargs) :
    def f(*args) :
      internal = {'args':args}
      for fstring in self.fstrings[:-1] :
        exec fstring in internal
      return eval(self.fstrings[-1], internal)
    result = f(*(tuple(self.args)+inargs))
    return result
