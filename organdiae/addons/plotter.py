"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

plotter.py: makes plots of piecewise polynomials using matplotlib

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

from ..core import OrgandiaeError
from ..core import Polynomial, PiecewisePolynomial

import pylab

def pwp_mpl(pw) :
  """
  Throw in in a piecewise polynomial...get out a pylab plot...
  Good times!
  
  .. note::
    Matplotlib MUST be installed for this to work!
  """
  xaranges = []
  yaranges = []
  for x in range(1,len(pw._polynomials)-1) :
    xaranges.append(pylab.arange(pw._pbounds[x],pw._pbounds[x+1],0.01))
    yrg = pylab.zeros(len(xaranges[-1]))
    for y in range(len(pw._polynomials[x]._coefficients)) :
      yrg += pw._polynomials[x]._coefficients[y]*(xaranges[-1]**y)
    yaranges.append(yrg)
  for x in range(len(xaranges)) :
    pylab.plot(xaranges[x], yaranges[x])
    
