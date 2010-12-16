"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

polynomial.py: implements a polynomial class in organdiae

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

import copy
import math
import sys
import bisect

"""
Known issues:
Convolution is poor for multiplication of functions (ie x is 3* longer than y)
  For this reason, better to consider result of conv as x in e**x
"""

OPTIMIZED = False

class NotEnoughInfoError(Exception) : pass

def fill_array(x,y,filler) :
  out = []
  for a in range(x) :
    out.append([filler]*y)
  return out

def zero_array(x,y) :
  return fill_array(x,y,0.)

def is_zero(a) :
  for x in a :
    if x != 0. :
      return False
  return True

def flattenList(x):
  result = []
  for el in x :
    if type(el) == type([]) :
      result.extend(flattenList(el))
    else :
      result.append(el)
  return result

def row_pascal(r) :
  out = [1]
  for c in range(1,r+1) :
    out += [int(out[-1]*((r+1.-c)/c))]
  return out
  
#KLUDGE! can do from math library

def fact(n) :
  out = 1
  while n > 1 :
    out *= n
    n -= 1
  return out

def sinO(iter=50) :
  c = ()
  s = 1
  for x in range(iter) :
    c += (0,s*1./fact((x*2)+1))
    s *= -1
  return Polynomial(c)

def eO(iter=50) :
  c = ()
  for x in range(iter) :
    c += (1./fact(x),)
  return Polynomial(c)

def cosO(iter=50) :
  c = ()
  s = 1
  for x in range(iter) :  
    c += (s*1./fact(x*2),0)
    s *= -1
  return Polynomial(c)

class Polynomial(object) :
  """
  Polynomial that behaves like a polynomial should under addition, subtraction, and multiplication.
  
  Example ::
  
    >>> from organdiae import *
    >>> p1 = Polynomial(3.,2.,0.,5.)
    >>> p2 = Polynomial(0.,-8.,1.)
    >>> print p1+p2
    (3.0, -6.0, 1.0, 5.0)
    >>> print p1-p2
    (3.0, 10.0, -1.0, 5.0)
    >>> print p1*p2
    (0.0, -24.0, -13.0, 2.0, -40.0, 5.0)
    >>> print p1**2
    (9.0, 12.0, 4.0, 30.0, 20.0, 0.0, 25.0)
  """
  def __init__(self, *args) :
    """
    Init, taking either a tuple with polynomial coefficients or the coefficients themselves.
    Coefficients are listed from the 0th to nth order.  So, Polynomial(1.,2.,0.,3.) is equivalent to 3.0*(x**2) + 2.0*x + 1.0.
    Example ::
    
      >>> from organdiae import *
      >>> p1 = Polynomial((1.,2.,3.))
      >>> print p1
      (1.0, 2.0, 3.0)
      >>> p2 = Polynomial(1.,2.,3.)
      (1.0, 2.0, 3.0)
      >>> print p2
      (1.0, 2.0, 3.0)
    """
    if (type(args[0]) == type([])) | (type(args[0]) == type(())) :
      self._coefficients = tuple(args[0])
    else :
      self._coefficients = args
  def __add__(self, p) :
    return self.__addsub__(p, 1)
  def __sub__(self, p) :
    return self.__addsub__(p, -1)
  def __addsub__(self, p, sign) :
    if len(p._coefficients) > len(self._coefficients) :
      p1 = p._coefficients
      p2 = self._coefficients + (0,)*(len(p._coefficients) - len(self._coefficients))
    else :
      p1 = self._coefficients
      p2 = p._coefficients + (0,)*(len(self._coefficients) - len(p._coefficients))
    new = ()
    for x in range(len(p1)) :
      new += (p1[x]+(p2[x]*sign),)
    return Polynomial(new)
  def __mul__(self, p) :
    out = [0.]*(len(p._coefficients)+len(self._coefficients)-1)
    for x in range(len(self._coefficients)) :
      for y in range(len(p._coefficients)) :
        out[x+y] += self._coefficients[x]*p._coefficients[y]
    return Polynomial(tuple(out))
  def __pow__(self, p) :
    out = Polynomial((1,))
    for x in range(p) :
      out = out*self
    return out
  def convolve(self, p) :
    """Same as multiplication."""
    return self*p
  def __str__(self) :
    return str(self._coefficients)
  def evaluate(self, n) :
    """
    Evaluates the polynomial at n
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.,2.,-3.,0.5)
      >>> p.evaluate(3.)
      -6.5
    """
    out = 0.0
    for x in range(len(self._coefficients)) :
      out += (n**x)*self._coefficients[x]
    return out
  def round(self, sig) :
    """
    Returns a new polynomial with coefficients rounded to `sig` significant figures.
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.111111111,2.,-3.,0.5)
      >>> print p.round(3)
      -6.5
    """
    coefficients = list(self._coefficients)
    for x in range(len(coefficients)) :
      coefficients[x] = round(coefficients[x], sig)
    return Polynomial(tuple(coefficients))
  def shift(self, amount) :
    """
    Returns a new polynomial shifted along the x axis by `amount`.
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.11,2.,-3.,0.5)
      >>> print p.shift(-2)
      (-2.89, -4.0, 0.0, 0.5)
    """
    amount *= -1
    coefficients = list(self._coefficients)
    for x in range(1, len(coefficients)) :
      p = row_pascal(x)
      for y in range(len(p)-1) :
        coefficients[y] += (amount**(len(p)-y-1))*p[y]*self._coefficients[x]
    return Polynomial(tuple(coefficients))
  def reflectY(self) :
    """
    Returns a new polynomial reflected about the y axis.
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.11,2.,-3.,0.5)
      >>> print p.reflectY()
      (1.11, -2.0, -3.0, -0.5)
    """
    new_c = ()
    for x in range(len(self._coefficients)) :
      if x%2 == 0 :
        new_c += (self._coefficients[x],)
      else :
        new_c += (-1*self._coefficients[x],)
    return Polynomial(new_c)
  def integrate(self,l,r) :
    """
    Integrates the polynomial from `l` to `r`.
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.11,2.,-3.,0.5)
      >>> print p.integrate(0,3.1415)
      -5.472746127
    """
    # Exception handling is kludge to take care of pinched edges from piecewise polynomial.
    # Will fix it to be more elegant...but it works...
    i = self.integral()
    return i.evaluate(r) - i.evaluate(l)
  def integral(self) :
    """
    Returns the indefinite integral, with 0.0 representing the constant
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.11,2.,-3.,0.5)
      >>> print p.integrate(0,3.1415)
      -5.472746127
    """
    return Polynomial(*tuple([0.]+[self._coefficients[x]/(x+1.) for x in range(len(self._coefficients))]))
  def lintegral(self, l) :
    """Return the Polynomial for a definite integral starting at point `l`."""
    i = self.integral()
    return i - Polynomial(i.evaluate(l))
  def differentiate(self) :
    """
    Returns a new polynomial that is a derivative of the current one.
    
    Example ::
      >>> from organdiae import *
      >>> p = Polynomial(1.11,2.,-3.,0.5)
      >>> print p.differentiate()
      (2.0, -6.0, 1.5)
    """
    new = list(self._coefficients[1:])
    for x in range(len(new)) :
      new[x] = new[x]*(1+x)
    return Polynomial(tuple(new))
  def asStr(self) :
    """
    Returns a pretty-print representation of the polynomial.
    """
    out = ''
    x = 0
    for c in self._coefficients :
      out += '('+str(c)+'*(x**'+str(x)+'))+'
      x += 1
    return out[:-1]
  def toGNUPlot(self, fn) :
    """
    Sends the polynomial to a gnuplot file named `fn`.  What you do with it is up to you.
    All of the examples in the help docs were generated via the svg viewer.
    """
    s = self.asStr()
    outFile = file(fn, 'w')
    outFile.write('f(x)='+s+'\nplot f(x)\n')
    outFile.close()
  def copy(self) :
    """
    Returns a copy of the current polynomial.
    """
    return Polynomial(self._coefficients)

class Impulse(object) :
  """
  A single impulse, to be used in piecewise polynomials.
  """
  def __init__(self, magnitude) :
    """Init takes single value of `magnitude` that is, not surprisingly, the magnitude of the impulse."""
    self._magnitude = magnitude
  def __str__(self) :
    return str(self._magnitude)
  def copy(self) :
    """Returns a copy of the impulse."""
    return Impulse(self._magnitude)
  def round(self, sig) :
    """Rounds the impulse to `sig` significant figures"""
    return Impulse(round(self._magnitude,sig))

class DeltaFunction(object) :
  """
  A representation of a piecewise polynomial given by [Polge73]_.  This allows for easy convolution.
  It is really not meant to be touched, and as such, the docstrings are very minimal.
  """
  def __init__(self, tuples=()) :
    for tup in tuples :
      if len(tup) != 3 : raise ValueError('tuples must have length 3')
    self._tuples = {}
    self.init_tuples(tuples)
  def __str__(self) :
    out = ''
    for x in self._tuples.keys() :
      out += str((self._tuples[x],)+x)+'\n'
    return out[:-1]
  def init_tuples(self, tuples) :
    for tuple in tuples :
      if tuple[0] == 0 : continue
      if not self._tuples.has_key(tuple[1:]) :
        self._tuples[tuple[1:]] = 0.
      self._tuples[tuple[1:]] += tuple[0]
    offenders = []
    for key in self._tuples.keys() :
      if self._tuples[key] == 0. : offenders.append(key)
    for offender in offenders :
      del(self._tuples[offender])
    if (len(self._tuples.keys()) == 0) & (len(tuples) > 0) :
      self._tuples[(0.,1)] = 0.
  def initialize(self, df) :
    if not self.isEmpty() :
      raise ValueError('Cannot initialize already-initialized DeltaFunction')
    for key in df._tuples.keys() :
      self._tuples[key] = df._tuples[key]
  def isEmpty(self) :
    """Like in ``Collection``, this implementation of ``isEmpty`` is used by the crawler to see if a delta function has been initialized."""
    if self._tuples == {} :
      return True
    return False
  def reset(self) :
    """Resets the delta function to nothing."""
    self._tuples = {}
  def piecewisePolynomial(self) :
    """Returns a a piecewise polynomial representation of the delta function."""
    if len(self._tuples.keys()) == 0 :
      return PiecewisePolynomial([Polynomial((0.,))],[None,()],[],[])
    if len(self._tuples.keys()) == 1 :
      stk = self._tuples.keys()[0]
      if stk[1] != 0 : raise ValueError('Go back to the piecewise polynomial code & fix this bug!')
      return PiecewisePolynomial([Polynomial((0.,))],[None,()],[Impulse(self._tuples[stk])],[stk[0]])      
    boundM = []
    width = 0
    impulses = []
    iplacements = []
    for key in self._tuples.keys() :
      if key[1] > width :
        width = key[1]
      if key[0] in boundM : continue
      boundM.append(key[0])
    boundM.sort()
    cmx = zero_array(len(boundM), width)
    smx = zero_array(len(boundM), width)
    tmx = zero_array(len(boundM)-1, width)
    emx = fill_array(width, width, (0.,0.))
    for x in range(len(emx)) :
      for y in range(x+1) :
        emx[x][y] = (1./(fact(x-y)*fact(y)), x-y)
    for key in self._tuples.keys() :
      if key[1] == 0 :
        impulses.append(Impulse(self._tuples[key]))
        iplacements.append(key[0])    
      else :
        cmx[boundM.index(key[0])][key[1]-1] = self._tuples[key]
    for x in range(len(cmx)) :
      for y in range(len(emx)) : 
        sum = 0.0
        for z in range(len(emx)) :
          sum += cmx[x][z]*(emx[z][y][0]*((-1*boundM[x])**emx[z][y][1]))
        smx[x][y] = sum
    try : tmx[0] = smx[0]
    except IndexError, e :
      print e
      print "SMX", smx
      print "L BOUNDM", len(boundM)
      print "L TUPLES", len(self._tuples.keys())
      sys.exit(0)
    for x in range(1, len(tmx)) :
      for y in range(len(emx)) : 
        tmx[x][y] = smx[x][y] + tmx[x-1][y]
    plist = []
    for l in tmx :
      plist.append(Polynomial(tuple(l)))
    return PiecewisePolynomial(plist, boundM, impulses, iplacements)
  def convolve(self, d) :
    """Convolves two delta functions, returning the result.  Consult the :ref:`first <first-concept>` of :doc:`concepts` to see this method in action."""
    new_t = []
    for k1 in self._tuples.keys() :
      for k2 in d._tuples.keys() :
        new_t.append((self._tuples[k1]*d._tuples[k2],k1[0]+k2[0],k1[1]+k2[1]))
    return DeltaFunction(new_t)
    
class PiecewisePolynomial(object) :
  """
  Representation of a piecewise polynomial using polynomials and impulses.  Behaves exactly like polynomials do.
  All piecewise polynomials are implicitly cropped at 0 on either end.
  
  Example ::
  
    >>> from organdiae import *
    >>> p1 = Polynomial(3.,2.,0.,5.)
    >>> p2 = Polynomial(0.,-8.,1.)
    >>> p3 = Polynomial(-3.,0.,0.,2.)
    >>> i1 = Impulse(2.0)
    >>> i2 = Impulse(-1.2)
    >>> pp1 = PiecewisePolynomial([p1,p2,p3],[-5.,4.,5.,6.],[],[])
    >>> pp2 = PiecewisePolynomial([p2,p3],[2.,3.,8.],[i1,i2],[0.,4.])
    >>> print pp1+pp2
    POLYNOMIALS ::: (0,), None, -5.0 >> (3.0, 2.0, 0.0, 5.0), -5.0, 2.0 >> (3.0, -6.0, 1.0, 5.0), 2.0, 3.0 >> (0.0, 2.0, 0.0, 7.0), 3.0, 4.0 >> (-3.0, -8.0, 1.0, 2.0), 4.0, 5.0 >> (-6.0, 0.0, 0.0, 4.0), 5.0, 6.0 >> (-3.0, 0.0, 0.0, 2.0), 6.0, 8.0 >> (0,), 8.0, () ;;; IMPULSES ::: 2.0, 0.0 >> -1.2, 4.
    >>> print pp1-pp2
    POLYNOMIALS ::: (0,), None, -5.0 >> (3.0, 2.0, 0.0, 5.0), -5.0, 2.0 >> (3.0, 10.0, -1.0, 5.0), 2.0, 3.0 >> (6.0, 2.0, 0.0, 3.0), 3.0, 4.0 >> (-3.0, 8.0, -1.0, 2.0), 4.0, 5.0 >> (0.0, 0.0, 0.0, 0.0), 5.0, 6.0 >> (-3.0, 0.0, 0.0, 2.0), 6.0, 8.0 >> (0,), 8.0, () ;;; IMPULSES ::: -2.0, 0.0 >> 1.2, 4.
    >>> print pp1*pp2
    POLYNOMIALS ::: (0.0,), None, 2.0 >> (0.0, -24.0, -13.0, 2.0, -40.0, 5.0), 2.0, 3.0 >> (-9.0, -6.0, 0.0, -9.0, 4.0, 0.0, 10.0), 3.0, 4.0 >> (0.0, 24.0, -3.0, 0.0, -16.0, 2.0), 4.0, 5.0 >> (9.0, 0.0, 0.0, -12.0, 0.0, 0.0, 4.0), 5.0, 6.0 >> (0.0,), 6.0, () ;;; IMPULSES ::: 6.0, 0.0 >> -397.2, 4.

  Note that multiplication, here, is different than convolution.
  Multiplication superimposes the two polynomials and multiplies their values.
  For convolution of PiecewisePolynomials, check out the ``DeltaFunction`` documentation.
  Exponentiation is not defined.
  """
  def __init__(self, polynomials=[], pbounds=[], impulses=[], iplacements=[]) :
    """
    Providing this init function with no options will get a PiecewisePolynomial that is in effect Polynomial(0.).
    For more interesting results:
    
    * `polynomials` contains the polynomials of the piecewise function IN ORDER from lowest to highest range.
    * `pbounds` provides the left and right bound for each polynomials.  Note that, by definition, the right bound of one is the left bound of another.  As such, pbounds must always be of length ``len(polynomials)+1``.
    * `impulses` contains single impulses.
    * `iplacements` tells the placement along the x-axis of each ``Impulse`` in `impulses`.  The length of this array must be the length of `impulses`.

    Failure to do the above will either result in an error message or, if you do something that I didn't anticipate, will result in wild behavior.
    """
    self._polynomials = []
    for polynomial in polynomials : self._polynomials.append(polynomial.copy())
    self._pbounds = []
    for bound in pbounds : self._pbounds.append(bound)
    self._impulses = []
    for impulse in impulses : self._impulses.append(impulse.copy())
    self._iplacements = []
    for iplacement in iplacements : self._iplacements.append(iplacement)
    self._iplacements = iplacements
    if (len(impulses) > 0) & (len(polynomials) == 0) :
      self._polynomials = [Polynomial((0.,))]
      self._pbounds = [None,()]
    elif (len(impulses) == 0) & (len(polynomials) == 0) : pass
    else :
      if self._pbounds[0] != None :
        self._pbounds = [None] + self._pbounds
        self._polynomials = [Polynomial((0,))]+self._polynomials
      else :
        if not is_zero(self._polynomials[0]._coefficients) :
          raise ValueError('left bound must be flat, not '+str(self._polynomials[0]))
      if self._pbounds[-1] != () :
        self._pbounds += [()]
        self._polynomials += [Polynomial((0,))]
      else :
        if not is_zero(self._polynomials[-1]._coefficients) :
          raise ValueError('right bound must be flat, not '+str(self._polynomials[-1]))
      self.validate()
      self.slim_zeros()
  def __getp(self, l, r) :
    for x in range(1,len(self._pbounds)) :
      if (l >= self._pbounds[x-1]) & (r <= self._pbounds[x]) :
        return x-1
    raise ValueError
  def __add__(self, p) :
    return self.__op(p, '__add__')
  def __sub__(self, p) :
    return self.__op(p, '__sub__')
  def __mul__(self, p) :
    return self.__op(p, '__mul__')
  def __op(self, p, op) :
    if self.isEmpty() | p.isEmpty() : raise NotEnoughInfoError
    if op not in ['__add__','__sub__','__mul__'] :
      raise ValueError
    pbounds = list(set(self._pbounds).union(set(p._pbounds)))
    pbounds.sort()
    polynomials = []
    for x in range(1,len(pbounds)) :
      p1 = self._polynomials[self.__getp(pbounds[x-1], pbounds[x])]
      p2 = p._polynomials[p.__getp(pbounds[x-1], pbounds[x])]
      polynomials.append(getattr(p1,op)(p2))
    impulse_d = {}
    impulses = []
    iplacements = []
    for x in range(len(self._iplacements)) :
      if not impulse_d.has_key(self._iplacements[x]) :
        impulse_d[self._iplacements[x]] = 0.
      if op == '__mul__' : 
        m = p._polynomials[p.__getp(self._iplacements[x], self._iplacements[x])].evaluate(self._iplacements[x])
      elif op == '__sub__' :
        m = 1.
      elif op == '__add__' :
        m = 1.
      impulse_d[self._iplacements[x]] += self._impulses[x]._magnitude*m
      if (op == '__mul__') & (self._iplacements[x] in p._iplacements) :
        xtra = self._impulses[x]._magnitude*p._impulses[p._iplacements.index(self._iplacements[x])]._magnitude
        impulse_d[self._iplacements[x]] += xtra
    for x in range(len(p._iplacements)) :
      if not impulse_d.has_key(p._iplacements[x]) :
        impulse_d[p._iplacements[x]] = 0.
      if op == '__mul__' : 
        m = self._polynomials[self.__getp(p._iplacements[x], p._iplacements[x])].evaluate(p._iplacements[x])
      elif op == '__sub__' :
        m = -1.
      elif op == '__add__' :
        m = 1.
      impulse_d[p._iplacements[x]] += p._impulses[x]._magnitude*m
      #impulse_d[p._iplacements[x]] = getattr(float(impulse_d[p._iplacements[x]]),op)(p._impulses[x]._magnitude)*m
    for key in impulse_d.keys() :
      impulses.append(Impulse(impulse_d[key]))            
      iplacements.append(key)
    return PiecewisePolynomial(polynomials, pbounds, impulses, iplacements)
  def __pow__(self, n) :
    out = PiecewisePolynomial([Polynomial(1.)],[self._pbounds[1],self._pbounds[-2]],[],[])
    for x in range(n) :
      out = out*self
    return out
  def __str__(self) :
    out = 'POLYNOMIALS ::: '
    for x in range(len(self._polynomials)) :
      out+= str(self._polynomials[x])+', '+str(self._pbounds[x])+', '+str(self._pbounds[x+1])+' >> '
    out = out[:-4]
    out += ' ;;; IMPULSES ::: '
    for x in range(len(self._impulses)) :
      out+= str(self._impulses[x])+', '+str(self._iplacements[x])+' >> '
    out = out[:-4]
    return out[:-1]
  def convolve(self, n) :
    """Shorthand for the following : ``self.deltaFunction().convolve(n.deltaFunction()).piecewisePolynomial()``"""
    return self.deltaFunction().convolve(n.deltaFunction()).piecewisePolynomial
  def evaluate(self, n) :
    """Evaluates the piecewise polynomial at value `n`"""
    if self.isEmpty() : raise NotEnoughInfoError
    p = self._polynomials[self.__getp(n,n)]
    out = p.evaluate(n)
    try :
      i = self._iplacements.index(n)
      out += self._impulses[i]._magnitude
    except : pass
    return out
  def round(self, sig) :
    """
    Returns a new piecewise polynomial with coefficients rounded to `sig` significant figures.
    Behaves just like its counterpart in ``Polynomial``.
    """
    if self.isEmpty() : raise NotEnoughInfoError
    polynomials = []
    pbounds = []
    impulses = []
    iplacements = []
    for x in range(1,len(self._polynomials)-1) :
      polynomials.append(self._polynomials[x].round(sig))
    for x in range(1,len(self._pbounds)-1) :
      pbounds.append(round(self._pbounds[x],sig))
    for x in range(len(self._iplacements)) :
      impulses.append(self._impulses[x].round(sig))
      iplacements.append(round(self._iplacements[x],sig))
    return PiecewisePolynomial(polynomials, pbounds, impulses, iplacements)
  def shift(self, amount) : 
    """
    Returns a new piecewise polynomial shifted along the x axis by `amount`.
    Behaves just like its counterpart in ``Polynomial``.
    """
    if self.isEmpty() : raise NotEnoughInfoError
    polynomials = []
    pbounds = []
    impulses = []
    iplacements = []
    for x in range(1,len(self._polynomials)-1) :
      polynomials.append(self._polynomials[x].shift(amount))
    for x in range(1,len(self._pbounds)-1) :
      pbounds.append(self._pbounds[x]+amount)
    for x in range(len(self._iplacements)) :
      impulses.append(self._impulses[x].copy())
      iplacements.append(self._iplacements[x]+amount)
    return PiecewisePolynomial(polynomials, pbounds, impulses, iplacements)
  def reflectY(self) :
    """
    Returns a new polynomial reflected about the y axis.
    Behaves just like its counterpart in ``Polynomial``.
    """  
    if self.isEmpty() : raise NotEnoughInfoError
    polynomials = []
    pbounds = []
    impulses = []
    iplacements = []
    for x in range(1,len(self._polynomials)-1) :
      polynomials.append(self._polynomials[x].reflectY())
    for x in range(1,len(self._pbounds)-1) :
      pbounds.append(self._pbounds[x]*-1)
    for x in range(len(self._iplacements)) :
      impulses.append(self._impulses[x].copy())
      iplacements.append(self._iplacements[x]*-1)
    polynomials.reverse()
    pbounds.reverse()
    impulses.reverse()
    iplacements.reverse()
    return PiecewisePolynomial(polynomials, pbounds, impulses, iplacements)
  def toGNUPlot(self, fn) :
    """
    Exports a piecewise polynomial to GNUPlot.  Behaves just like its counterpart in ``Polynomial``.
    """
    if self.isEmpty() : raise NotEnoughInfoError
    out = 'f(x) = x < '+str(self._pbounds[1])+' ? 0 : '
    for x in range(1,len(self._polynomials)-1) :
      out += ' x < '+str(self._pbounds[x+1])+' ? '+self._polynomials[x].asStr()+' : '
    out += ' 0\nplot ['+str(self._pbounds[1])+':'+str(self._pbounds[-2])+'] f(x)'
    outFile = file(fn, 'w')
    outFile.write(out)
    outFile.close()    
  def validate(self) :
    if len(self._pbounds) != 1+len(self._polynomials) :
      raise ValueError
    if len(self._iplacements) != len(self._impulses) :
      raise ValueError
    test = copy.deepcopy(self._pbounds)
    test.sort()
    if test != self._pbounds :
      raise ValueError
  def slim_zeros(self) :
    for x in range(1,len(self._polynomials)-1) :
      if self._polynomials[x]._coefficients == (0,)*len(self._polynomials[x]._coefficients) :
        self._polynomials = self._polynomials[:x]+self._polynomials[x+1:]
        self._pbounds = self._pbounds[:x] + self._pbounds[x+1:]
        self.slim_zeros()
        break
      else :
        break
    rev = range(1,len(self._polynomials)-1)
    rev.reverse()
    for x in rev :
      if self._polynomials[x]._coefficients == (0,)*len(self._polynomials[x]._coefficients) :
        self._polynomials = self._polynomials[:x]+self._polynomials[x+1:]
        self._pbounds = self._pbounds[:x+1] + self._pbounds[x+2:]
        self.slim_zeros()
        break
      else :
        break
  def coefficientMatrix(self) :
    max_l = 0 
    for polynomial in self._polynomials :
      if len(polynomial._coefficients) > max_l :
        max_l = len(polynomial._coefficients)
    m = zero_array(len(self._polynomials), max_l)
    for x in range(len(self._polynomials)) :
      for y in range(len(self._polynomials[x]._coefficients)) :
        m[x][y] = self._polynomials[x]._coefficients[y]
    return m
  def boundMatrix(self) :
    m = []
    for bound in self._pbounds :
      m.append([bound])
    return m
  def deltaFunction(self) :
    """Returns a delta function version of the piecewise polynomial.  Useful in convolution."""
    if self.isEmpty() : raise NotEnoughInfoError
    coefficientM = self.coefficientMatrix()
    boundM = self.boundMatrix()[1:-1]
    cmx = zero_array(len(coefficientM)-1, len(coefficientM[0]))
    smx = zero_array(len(coefficientM)-1, len(coefficientM[0]))
    emx = fill_array(len(coefficientM[0]), len(coefficientM[0]), (0.,0.))
    for x in range(1, len(coefficientM)) :
      for y in range(len(emx)) : 
        smx[x-1][y] = coefficientM[x][y] - coefficientM[x-1][y]
    for x in range(len(emx)) :
      for y in range(x+1) :
        emx[x][y] = (fact(x)*1./fact(x-y), x-y)
    for x in range(len(cmx)) :
      for y in range(len(emx)) : 
        sum = 0.0
        for z in range(len(emx)) :
          sum += smx[x][z]*(emx[z][y][0]*(boundM[x][0]**emx[z][y][1]))
        cmx[x][y] = (sum,boundM[x][0],y+1)
    impulses = []
    for x in range(len(self._impulses)) :
      impulses.append((self._impulses[x]._magnitude, self._iplacements[x], 0)) 
    return DeltaFunction(flattenList(cmx)+impulses)
  def integral(self) :
    """
    Spits out the cumulative distribution function of the ``PiecewisePolynomial``, discarding impulses
    (may be considered a bug by some...but for the moment I can't figure out a better way to implement it).
    """
    iparts = [self._polynomials[x].integrate(self._pbounds[x], self._pbounds[x+1]) for x in range(1, len(self._pbounds)-3)]
    iparts = [0] + iparts
    ints = [self._polynomials[x].integral() for x in range(1, len(self._pbounds)-2)]
    difs = [sum(iparts[0:x+1])-ints[x].evaluate(self._pbounds[x+1]) for x in range(len(self._pbounds)-3)]
    isps = [self._polynomials[x].integral()+Polynomial(difs[x-1]) for x in range(1, len(self._pbounds)-2)]
    return PiecewisePolynomial(isps, self._pbounds[1:-1],[],[])
  @staticmethod
  def rf(f, s,t,e,m) :
  # lifted from http://en.wikipedia.org/wiki/False_position_method
    side = 0
    fs = f(s)
    ft = f(t)
    for x in range(1,m+1) :
      r = ( (fs*t) - (ft*s) ) / (fs - ft)
      if abs(t-s) < (e*abs(t+s)) : break
      fr = f(r)
      if (fr * ft) > 0 :
        t = r
        ft = fr
        if side == -1 : fs /= 2
        side = -1
      elif (fs * fr) > 0 :
        s = r
        fs = fr
        if side == 1 : ft /= 2
        side = 1
      else : break
    return r
  def g0integrator(self, v, n=False) :
    """
    Solver for piecewise polynomials that never have negative area.
    `v` is the area you want, and the return value will give you the x you need to get that area.
    VERY strange results otherwise... ::
    
      >>> from organdiae import *
      >>> p = PiecewisePolynomial([Polynomial(11.,2.,3.,-0.25),Polynomial(0.3,2.,2.),Polynomial(0.3,2.3)],[-1.,4.,5.,6.],[],[])
      >>> p.integrate().evaluate(4.1)
      123.18316666666665
      >>> p.g0integrator(123.18316666666665)
      4.0999999999999996
      
    OK so it's not perfect...but almost!  Set `n` to if your v is 0-1 normalized.
    """
    iparts = [self._polynomials[x].integrate(self._pbounds[x], self._pbounds[x+1]) for x in range(1, len(self._pbounds)-3)]
    iparts = [0] + iparts
    ipsum = [sum(iparts[0:x+1]) for x in range(len(iparts))]
    if n : v = (v*ipsum[-1])+self._pbounds[1]
    if v < 0 : raise ValueError('Told you it would fail for non-positive areas.')
    if v > ipsum[-1] : raise ValueError('The area never gets this big...')
    bl = bisect.bisect_left(ipsum, v)
    br = bisect.bisect_right(ipsum,v)
    if bl != br : return self._pbounds[bl+2]
    tobesolved = self._polynomials[bl].lintegral(self._pbounds[bl])-Polynomial(v-ipsum[bl-1])
    return PiecewisePolynomial.rf(tobesolved.evaluate,self._pbounds[bl],self._pbounds[bl+1],5E-15,100)
  def reset(self) :
    """
    Resets the piecewise polynomial to contain nothing.
    """
    self._polynomials = []
    self._pbounds = []
    self._impulses = []
    self._iplacements = []
  def isEmpty(self) :
    """Checks to see if the piecewise polynomial has been initialized."""
    if self._polynomials != [] : return False
    if self._pbounds != [] : return False
    if self._impulses != [] : return False
    if self._iplacements != [] : return False
    return True
  def initialize(self, p) :
    """
    Initializes a piecewise polynomial with the values of another one.
    """
    if not self.isEmpty() :
      raise ValueError('Cannot initialize an already-initialized polynomial')
    for x in range(len(p._polynomials)) :
      self._polynomials.append(p._polynomials[x].copy())
    for x in range(len(p._pbounds)) :
      self._pbounds.append(p._pbounds[x])
    for x in range(len(p._iplacements)) :
      self._impulses.append(p._impulses[x].copy())
      self._iplacements.append(p._iplacements[x])
  def scale(self, scalar) :
    """Returns a scaled version of the piecewise polynomial by factor `scalar`"""
    if self.isEmpty() : raise NotEnoughInfoError
    return self * PiecewisePolynomial([Polynomial((scalar,))], [self._pbounds[1], self._pbounds[-2]])
  def normalizeIntegral(self) :
    """Returns a version of the piecewise polynomial so that the area under it sums up to 1."""
    if self.isEmpty() : raise NotEnoughInfoError
    integral = sum([self._polynomials[x].integrate(self._pbounds[x], self._pbounds[x+1]) for x in range(1, len(self._pbounds)-3)])
    if integral == 1.0 :
      return self
    elif integral == 0.0 :
      return self
    else :
      return self.scale(1./integral)
  def __eq__(self, other) :
    try :
      if len(self._polynomials) != len(other._polynomials) : return False
      for x in range(len(self._polynomials)) :
        if len(self._polynomials) != len(other._polynomials) : return False
        for y in range(len(self._polynomials[x]._coefficients)) :
          if self._polynomials[x]._coefficients[y] != other._polynomials[x]._coefficients[y] : return False
      if self._pbounds != other._pbounds : return False
      if len(self._impulses) != len(other._impulses) : return False
      for x in range(len(self._impulses)) :
        if self._impulses[x]._magnitude != other._impulses[x]._magnitude : return False
      if self._iplacements != other._iplacements : return False
      return True
    except Exception, e: 
      return False

