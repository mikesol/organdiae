"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

bootstrap.py: generates the bootstrap file for organdiae
sessions

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

import os
from optparse import OptionParser
import sys

def bs(path, nbuses = [], cbuses = []) :
  """
  Generates a bootstrap file at `path` for an organdiae session and loads pertinant variables into global namespace.
  
  Arugments:

  `path`
    The path of the file (.py will be automatically appended)
  `nbuses`
    A list of numerical buses to create in the standard bus function.
  `cbuses`
    A list of collection buses to create in the standard bus function.
  
  Elements of both `nbuses` and `cbuses` should be single words beginning with capital letters, as they will be transformed into classes in the global namespace.
  
  Example usage: ::
  
    >>> from organdiae import *
    >>> bs('foo', nbuses=['Weight'], cbuses=['Information'])
    >>> sb()
    {<class 'organdiae.core.core.Tags'>: <organdiae.core.core.CFunction object at 0x780930>, <class 'organdiae.core.core.Information'>: <organdiae.core.core.CFunction object at 0x1052e10>, <class 'organdiae.core.core.Weight'>: <organdiae.core.core.CFunction object at 0x1052e30>}  
  """
  if len(list(set(nbuses))) != len(nbuses) : raise ValueError('NBuses must have unique values')
  if len(list(set(cbuses))) != len(cbuses) : raise ValueError('CBuses must have unique values')
  if os.path.exists(path+'.py') : raise OSError("Can't overwrite session...")
  outfi = file(path+'.py', 'w')
  bigstr = """#!/usr/bin/python
# Autogenerated organdiae bootstrap file

from organdiae import *
import sys

try : unPickMe('"""+path+""".oie')
except : pass

nbuses = """+str(nbuses)+"""
cbuses = """+str(cbuses)+"""

if not nbuses :
  nbuses = []
if not cbuses : 
  cbuses = []

for bus in cbuses+['Tags'] :
  if bus not in sys.modules['__main__'].__dict__ :
    ng(bus, name=True, return_type = Collection)

for bus in nbuses :
  if bus not in sys.modules['__main__'].__dict__ :
    ng(bus, name=True, return_type = PiecewisePolynomial)

def sb(*args, **kwargs) : 
  '''
  Generates a standard bus for an Edge
  All arguments are thrown into a Tags bus.
  
  Additionally, the user has defined the following busses:
    Numerical :::  """+str(cbuses)+"""
    Collection ::: """+str(nbuses)+"""
  '''
  od = {}
  od[sys.modules['__main__'].__dict__['Tags']] = CFunction(['a = args[0] + args[1]', 'a'],
                                          (Collection(set(args)),))
  try :
    np = nbuses + kwargs['nbuses']
  except :
    np = nbuses
  try :
    cp = cbuses + kwargs['cbuses']
  except :
    cp = cbuses
  for x in cp :
    od[sys.modules['__main__'].__dict__[x]] = CFunction(['a = args[0] + args[1]', 'a'],
                                          (Collection(set([])),))                                        
  for x in np :
    od[sys.modules['__main__'].__dict__[x]] = CFunction(['a = (args[0].deltaFunction().convolve(args[1].deltaFunction())).piecewisePolynomial()','a'],
                                          (PiecewisePolynomial([],[],[Impulse(1.0)],[0.0]),))
  return od

def pick() : 
  '''
  Saves all of the DiGraph instances in the interpreter.
  '''
  pd = {}
  for item in sys.modules['__main__'].__dict__ :
    if isinstance(sys.modules['__main__'].__dict__[item], DiGraph) :
      pd[item] = sys.modules['__main__'].__dict__[item]
      continue
    try :
      if issubclass(sys.modules['__main__'].__dict__[item], DiGraph) :
        pd[item] = sys.modules['__main__'].__dict__[item]
    except : pass  
  pickMe('"""+path+""".oie', pd)

def labeling_scheme(e) :
  '''
  Labeling scheme for gv
  '''
  s = ''
  try :
    for x in e._f[sys.modules['__main__'].__dict__['Tags']].args[0].s : s += x.ilsagitde+' ::: '
    if len(s) > 0 : s = ',label="'+s[:-5]+'"'
    if len(s) == 0 : s = ',label="i was too lazy to label this edge"'
  except KeyError : 
    s = ',label="i was too lazy to label this edge"'
  return s

def gv(g, **kwargs) :
  '''
  Friendly talker to the GraphViz backend
  '''
  path = '"""+path+"""'
  if 'path' in kwargs :
    path = kwargs['path']
    del kwargs['path']
  DiGraph.toGraphViz(g, path, labeling_scheme=labeling_scheme, **kwargs)

def gettag(e) :
  return list(e._f[sys.modules['__main__'].__dict__['Tags']].args[0].s)[0]

F = Forest
T = Tree
V = Vertex
E = Edgeless
PP = PiecewisePolynomial
P = Polynomial
I = Impulse
D = DeltaFunction
CF = CFunction
C = Collection
"""
  outfi.write(bigstr)
  outfi.close()
  exec bigstr in sys.modules['__main__'].__dict__

if __name__ == '__main__' :
  usage = "usage: %prog [options] session_name"
  parser = OptionParser(usage=usage, version="%prog 0.0")

  parser.add_option("-n","--numerical", action="append",help="add a numerical bus to the standard bus group")
  parser.add_option("-c","--collection", action="append",help="add a collection bus to the standard bus group")

  (options, args) = parser.parse_args()

  if len(args) == 0 :
    raise ValueError("You need to supply this script with a session name so that it can do its thing.")
    
  if len(args) > 1 :
    raise ValueError("You need to supply this script with ONE session name so that it can do its thing, not multiple.")

  bs(args[0], options.numerical, options.collection)