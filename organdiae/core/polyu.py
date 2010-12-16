"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

polyu.py: utilities for polynomials

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

from polynomial import PiecewisePolynomial, Polynomial
from core import OrgandiaeError

def bpc(xy, *args, **kwargs) :
  """
  Usage ::

    from organdiae import *
    a = polyu.bpc((-2,3),(2,3,1),(2,-3,0),(2,-3,1),(2,3,0),(2,3,1), pw=3)
    b = polyu.bpc((-2,3),(2,3,1,2),(2,-3,0,3),(2,-3,1,1),(2,3,0,2),(2,3,1,4))
    c = polyu.bpc((-2,3),(2,3),(2,-3),(2,-3),(2,3),(2,3))
  
  Where the...
  
  * first tuple signifies where the start point is (x,y)
  * each tuple afterwards contains (x_displacement, y_displacement, [0,1] -> [leaving fast, leaving slow])
  
  Optional 4th argument in the tuple is the power.  If this is set for one tuple, it must be set for all of them and pw will be ignored.
  If this not set, make sure to put pw=n where n is an integer >= 0
  Tuples of 2 will get a straight line irrespective of the power argument.
  """
  return _bpcore(xy, True, *args, **kwargs)

def bpcd(xy, *args, **kwargs) :
  """
  Usage ::

    from organdiae import *
    a = polyu.bpcd((-2,3),(2,6,1),(2,3,0),(2,0,1),(2,3,0),(2,6,1), pw=3)
    b = polyu.bpcd((-2,3),(2,6,1,2),(2,3,0,3),(2,0,1,1),(2,3,0,2),(2,6,1,4))
    c = polyu.bpcd((-2,3),(2,6),(2,3),(2,0),(2,3),(2,6))
  
  Where the...
  
  * first tuple signifies where the start point is (x,y)
  * each tuple afterwards contains (x_displacement, y_position, [0,1] -> [leaving fast, leaving slow])
  
  Optional 4th argument in the tuple is the power.  If this is set for one tuple, it must be set for all of them and pw will be ignored.
  If this not set, make sure to put pw=n where n is an integer >= 0
  Tuples of 2 will get a straight line irrespective of the power argument.
  """
  dummy = (xy,) + args
  args = tuple([(dummy[x][0],dummy[x][1]-dummy[x-1][1])+dummy[x][2:] for x in range(1,len(dummy))])
  return _bpcore(xy, True, *args, **kwargs)

def bp(xy, *args, **kwargs) :
  """
  Usage ::
  
    a = polyu.bp((-2,3),(0,2,3,1),(-1,2,-3,0),(0,2,-3,1),(1,2,3,0),(0,2,3,1), pw=3)
    b = polyu.bp((-2,3),(0,2,3,1,2),(-1,2,-3,0,3),(0,2,-3,1,1),(1,2,3,0,2),(0,2,3,1,4))
    c = polyu.bp((-2,3),(0,2,3),(-1,2,-3),(0,2,-3),(1,2,3),(0,2,3))
  
  Where the...

  * first tuple signifies where the start point is (x,y)
  * each tuple afterwards contains (y_offset, x_displacement, y_displacement, [0,1] -> [leaving fast, leaving slow])

  Optional 4th argument in the tuple is the power.  If this is set for one tuple, it must be set for all of them and pw will be ignored.
  If this not set, make sure to put pw=n where n is an integer >= 0
  Tuples of 2 will get a straight line irrespective of the power argument.
  """
  return _bpcore(xy, False, *args, **kwargs)

def bpd(xy, *args, **kwargs) :
  """
  Usage ::

    a = polyu.bpd((-2,3),(0,2,6,1),(-1,2,3,0),(0,2,0,1),(1,2,3,0),(0,2,6,1), pw=3)
    b = polyu.bpd((-2,3),(0,2,6,1,2),(-1,2,3,0,3),(0,2,0,1,1),(1,2,3,3,2),(0,2,6,1,4))
    c = polyu.bpd((-2,3),(0,2,6),(-1,2,3),(0,2,0),(1,2,3),(0,2,6))
  
  Where the...
  
  * first tuple signifies where the start point is (x,y)
  * each tuple afterwards contains (y_offset, x_displacement, y_position, [0,1] -> [leaving fast, leaving slow])
  
  Optional 4th argument in the tuple is the power.  If this is set for one tuple, it must be set for all of them and pw will be ignored.
  If this not set, make sure to put pw=n where n is an integer >= 0
  Tuples of 2 will get a straight line irrespective of the power argument.
  """
  dummy = ((0,)+xy,) + args
  args = tuple([dummy[x][0:2]+(dummy[x][2]-dummy[x-1][2],)+dummy[x][3:] for x in range(1,len(dummy))])
  return _bpcore(xy, False, *args, **kwargs)

def _bpcore(xy, c, *args, **kwargs) :
  if len(xy) != 2 : raise OrgandiaeError('xy must be of length 2')
  len_check = set()
  args = list(args)
  for x in args :
    len_check.add(len(x))
  if len(len_check) > 1 : raise OrgandiaeError('Length of args need to be the same')
  cup = lambda c, v : v if c else v+1
  if list(len_check)[0] == cup(c,2) :
    for x in range(len(args)) :
      args[x] += (0,1)
  elif list(len_check)[0] == cup(c,3) :
    if kwargs.has_key('pw') : 
      pw = kwargs['pw']
    else :
      pw = 1
    for x in range(len(args)) :
      args[x] += (pw,)
  bounds = []
  args[0] = xy+args[0] if c else (xy[0],xy[1]+args[0][0]) + args[0][1:]
  bounds.append(args[0][0])
  for x in range(1,len(args)) :
    args[x] = (args[x-1][0]+args[x-1][2],args[x-1][1]+args[x-1][3])+args[x] if c else (args[x-1][0]+args[x-1][2],args[x-1][1]+args[x-1][3]+args[x][0])+args[x][1:]
    bounds.append(args[x][0])
  bounds.append(bounds[-1]+args[x][2])
  polys = []
  for x in range(len(args)) :
    if args[x][4] == 0 :
      a = Polynomial((-1*args[x][0],1))*Polynomial((1./args[x][2],))
      a = a**args[x][5]
      a = a*Polynomial((args[x][3],))
      a = a+Polynomial((args[x][1],))
      polys.append(a)
    elif args[x][4] == 1 :
      a = Polynomial((-1*(args[x][0]+args[x][2]),1))*Polynomial((1./args[x][2],))
      a = a**args[x][5]
      a = a*Polynomial((args[x][3]*((-1)**(args[x][5]-1)),))
      a = a+Polynomial((args[x][1]+args[x][3],))
      polys.append(a)
    else : 
      print args[x]
      raise OrgandiaeError
  return PiecewisePolynomial(polys, bounds, [],[])