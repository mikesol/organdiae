"""
organdiae- A mind mapping tool for the Python interpreter.
Copyright (C) 2010 Mike Solomon

core.py: core classes for organdiae

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

import random
import string
import sys
import os
import shutil
import re
import subprocess

try :
  import cPickle as pickler
except ImportError :
  import pickle as pickler

from polynomial import Polynomial, PiecewisePolynomial
from polynomial import Impulse
from polynomial import DeltaFunction
from polynomial import NotEnoughInfoError

CLASS_HEIRARCHY = []

def _randString(length=40, chars=string.letters + string.digits):
    first = random.choice(string.letters[26:])
    return first+''.join([random.choice(chars) for i in range(length-1)])

def which(program):
  import os
  def is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath,os.X_OK)
  fpath,fname=os.path.split(program)
  if fpath:
    return is_exe(program)
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      exe_file=os.path.join(path,program)
      if is_exe(exe_file):
        return True
  return False

def flatten(s) :
  result = []
  for x in s :
    if hasattr(x, "__iter__") and not isinstance(x, basestring) :
      result.extend(flatten(x))
    else :
      result.append(x)
  return result

def pickMe(path, main_d) :
  """
  Pickles a dictionary of items at `path`, pickling the organdiae class heirarchy as well.
  Used by the template created by bootstrap to save all graphs in a session.
  
  Arguments:
  
  `path`
    The path of the file you want to pickle to (two files, `path`.classdefs and `path`.normal, will be created)
  `main_d`
    Dictionary of stuff to save.
  
  Should be used with ``unPickMe`` to get data back.
  
  Example: ::
  
    >>> from organdiae import *
    >>> g = DiGraph()
    >>> g.av(ng('hello', name=True))
    >>> g.av(ng('world', name=True))
    >>> g.ae(hello, world)
    >>> pickMe('foo.oie', {'g':g})
    WRITING g TO foo.oie
    >>> quit()
    [start python again...]
    >>> from organdiae import *
    >>> unPickMe('foo.oie')
    >>> g.p()
    VERTICES
         0. hello
         1. world
    EDGES
         0. hello --> world  

  A much more satisfying and harmonious way to do this, that uses pickMe and unPickMe internally, is as follows ::
  
    >>> from organdiae import *
    >>> bs('foo')
    >>> g = DiGraph()
    >>> g.av(ng('hello', name=True))
    >>> g.av(ng('world', name=True))
    >>> sentence = ng('sentence')
    >>> g.ae(hello, world, sb(sentence))
    >>> pick()
    WRITING g TO foo.oie
    >>> quit()
    [start python again...]
    >>> from foo import *
    >>> g.p()
    VERTICES
         0. hello
         1. world
    EDGES
         0. hello --> world  
  """
  out_d = {}
  for key in main_d.keys() :
    if isinstance(main_d[key], DiGraph) : 
      print "WRITING", key, "TO", path
      out_d[key] = main_d[key]
  outfi = file(path+'.normal', 'wb')
  pickler.dump(out_d, outfi)
  outfi.close()
  outfi = file(path+'.classdefs', 'wb')
  offenders = []
  for x in range(len(CLASS_HEIRARCHY)-1) :
    for y in range(x+1,len(CLASS_HEIRARCHY)) :
      if CLASS_HEIRARCHY[x] == CLASS_HEIRARCHY[y] : offenders.append(y)
  offenders = list(set(offenders))
  for x in range(len(offenders)) :
    offenders[x] = CLASS_HEIRARCHY[offenders[x]]
  for offender in offenders :
    CLASS_HEIRARCHY.remove(offender)
  for x in range(len(CLASS_HEIRARCHY)) :    
    element = CLASS_HEIRARCHY[x]
    if element[1] in main_d :
      dc = main_d[element[1]].__dict__.copy()
      isd = dc['ilsagitde'] 
      del dc['__module__']
      del dc['__doc__']
      CLASS_HEIRARCHY[x] = (isd,CLASS_HEIRARCHY[x][1],CLASS_HEIRARCHY[x][2],dc,)
  pickler.dump(CLASS_HEIRARCHY, outfi)
  outfi.close()

def unPickMe(path) :
  """
  Unpickles a dictionary of items at `path`, unpickling the organdiae class heirarchy as well.
  Used by the template created by bootstrap to load all graphs in a session.
  
  Arguments:
  
  `path`
    The path of the file you want to unpickle (should be the same path you used for pickMe).
  
  Should be used with ``pickMe`` to save data.  See ``pickMe`` docstring for more info...
  """  
  infi = file(path+'.classdefs', 'rb')
  ch = pickler.load(infi)
  infi.close()
  for item in ch : 
    if type(item[2]) == type(type) : ng(item[0], name=item[1], dg=item[2], **item[3])
    else : ng(item[0], name=item[1], dg=globals()[item[2]], **item[3])
  infi = file(path+'.normal', 'rb')
  out_d = pickler.load(infi)
  infi.close()
  for key in out_d :
    setattr(sys.modules['__main__'], key, out_d[key])

class OrgandiaeError(Exception) : pass
class AddError(OrgandiaeError) : pass
class RemoveError(OrgandiaeError) : pass
class InsertError(OrgandiaeError) : pass

class _OrgandiaeObject(object) :
  def __init__(self, name=None) :
    if not name :
      name = _randString()
    self.__name__ = name

class Edge(_OrgandiaeObject) :
  """
  An edge from v1 to v2 with buses traveling along f.
  """
  def __init__(self, v1, v2, f={}, name=None) :
    """
    Init function for the edge.
    
    Arguments:
    
    `v1`
      Vertex from which edge provenes.
    `v2`
      Vertex to which edge goes.
    `f`
      A dictionary of DiGraph classes/subclasses and CFunctions
    `name`
      (optional - don't use)
    """
    _OrgandiaeObject.__init__(self, name)
    self._v1 = v1
    self._v2 = v2
    self._f = f
    self._cf = {}
    for kw in self._f :
      self._cf[kw] = kw.return_type()
  def ab(self,b,f) :
    """
    Adds a bus b that executes f along this edge.
    
    Arguments:
    
    `b`
      A subclass of DiGraph with return_type defined in its dictionary
    `f`
      A CFunction that returns return_type
    """
    if b in self._f.keys() : 
      raise OrgandiaeError('This already exists: try rb')
    self._f[b] = f
    self._cf[b] = b.return_type()
  def rb(self,b,f) :
    """
    Replaces a bus b that executes f along this edge.
    
    Arguments:
    
    `b`
      A subclass of DiGraph with return_type defined in its dictionary
    `f`
      A CFunction that returns return_type
    """
    if not f in self._f.keys() : 
      raise OrgandiaeError("This doesn't exist: try ab")
    self._f[f] = c
    self._cf[f] = f.return_type()
    
class DiGraph(_OrgandiaeObject) :
  """
  DiGraph is the lifeblood of Organdiae.  It has been rewritten hundreds of times in all shapes and sizes and is under active development.
  """
  ilsagitde = 'DiGraph'
  def __init__(self, ilsagitde = '', name = None, filters = []) :
    """
    Init function for DiGraph.

    Arguments:
    
    `ilsagitde`
      Human readable "thing" that this digraph is.  Often times, is a filepath to an image, audio clip, etc...
    `filters`
      A list of ``Filter`` classes that control the growth of the ``DiGraph`` instance.
    """
    _OrgandiaeObject.__init__(self, name)
    if not ilsagitde :
      ilsagitde = self.__class__.ilsagitde+' (hash '+str(self.__hash__())+')'
    self.ilsagitde = ilsagitde
    self._v = set([])
    self._e = set([])
    self._v1 = {}
    self._v2 = {}
    self._filters = set(filters)
  def __call__(self) : return self.ilsagitde
  @staticmethod 
  def po(offset, *args) :
    print " "*offset,
    for arg in args : 
      print arg,
    print ""
  def pv(self, offset = 0) :
    """
    A giant, verbose printing, meant for debugging.  When all else fails, dump this to a file and surf through it to see if the system is behaving as expected.
    """
    DiGraph.po(offset, self.__name__, ":::", self.ilsagitde)
    DiGraph.po(offset, "VERTICES")
    _v = list(self._v)
    for x in range(len(_v)) :
      v = _v[x]
      if type(v) == type(type) :
        DiGraph.po(offset, " "*4, str(x)+".", v.__name__, ":::", v.ilsagitde)
      else :
        v.pv(offset+5)
    DiGraph.po(offset, "VERTICES")
    _e = list(self._e)
    for x in range(len(_e)) :
      e = _e[x]
      DiGraph.po(offset, " "*4, str(x)+".", e._v1.ilsagitde, "-->", e._v2.ilsagitde)
      for kw in e._f :
        DiGraph.po(offset, " "*8, kw.__name__, kw.ilsagitde)
        DiGraph.po(offset, " "*8, "FN")
        for fs in e._f[kw].fstrings :
          DiGraph.po(offset, " "*12, fs)
        DiGraph.po(offset, " "*8, "ARGS")
        for arg in e._f[kw].args :
          DiGraph.po(offset, " "*12, arg)
  def p(self, regex=None, r=False) :
    """
    Prints the current contents of the digraph, filtering each element's ``ilsagitde`` by `regex` if provided.
    """
    if regex : regex = re.compile(regex)
    print "VERTICES"
    _v = list(self._v)
    _ov = []
    for x in range(len(_v)) :
      v = _v[x]
      if regex :
        if not regex.search(v.ilsagitde) : continue
      _ov.append(v)
      print " "*4, str(x)+".", v.ilsagitde
    print "EDGES"
    _e = list(self._e)
    _oe = []
    for x in range(len(_e)) :
      e = _e[x]
      if regex :
        if (not regex.search(e._v1.ilsagitde)) & (not regex.search(e._v2.ilsagitde)) : continue
      _oe.append(e)
      print " "*4, str(x)+".", e._v1.ilsagitde, "-->", e._v2.ilsagitde
    if r : return _ov,_oe
    if regex : return _ov,_oe
  def g(self, *args) :
    """
    The swiss army knife of getting.  Arguments tell where to look in the digraph.
    First, invoke ``p`` (potentially with a ``regex``) to see what's in the DiGraph instance.  Then...
    
    * ``dg.v(0)`` returns the vertex set.  ``dg.v(0,X)`` returns the X element of said set's list implementation.
    * ``dg.v(1)`` returns the edge set. ``dg.v(1,X)`` returns the X element of said set list implementation.
    * ``dg.v(1,X,Item,0)`` returns the CFunction at bus ``Item``.
    * ``dg.v(1,X,Tiem,1)`` returns the result of the CFunction from the most recent crawl (may be empty).
    """
    if args[0] == 0 :
      if len(args) == 1 : return self._v
      return list(self._v)[args[1]]
    elif args[0] == 1 :
      if len(args) == 1 : return self._e
      e = list(self._e)[args[1]]
      if len(args) == 2 : return e
      if type(args[2]) == type(0) :
        if args[2] == 0 : return e._v1
        if args[2] == 1 : return e._v0
      elif type(args[2]) == type(type) :
        if args[3] == 0 : return e._f[args[2]]
        else : return e._cf[args[2]]
      return None      
  def af(self, f) :
    """Add ``Filter`` `f` to the ``DiGraph`` instance."""
    if f.__class__ == Filter : pass
    else :
      for filter in self._filters :
        if filter.__class__ == f.__class__ :
          print "No two filters of the same class can be added save the class filter, to be used for anonymous filters."
          return False
    self._filters.add(f)
    return True
  def df(self, f) :
    if type(f) == type(0) : 
      self._filters.remove(self._filters[f])
    else :
      self._filters.remove(f)
  def av(self, v) :
    """Add vertex `v` to current ``DiGraph`` instance, where `v` is a subclass of ``DiGraph or an instance of a subclass of ``DiGraph``."""
    self.avs(v)
  def avs(self, *vs) :
    """Add list of vertices `vs` to current ``DiGraph`` instance, where each ``v`` in `vs` is a subclass of ``DiGraph`` or an instance of a subclass of ``DiGraph``."""
    vs = list(vs)
    for v in vs :
      if v in self._v :
        raise AddError('Vertex already in system, cannot add.')
      try :
        if type(v) == type(DiGraph) :
          if (not issubclass(v, DiGraph) ) :
            raise AddError('Vertex must be instance or subclass of DiGraph.')
        elif not isinstance(v, DiGraph) :
          raise AddError('Vertex must be instance or subclass of DiGraph.')
      except TypeError :
          raise AddError('Vertex must be instance or subclass of DiGraph.')
    important_filters = Filter.find_minimum_filter_list(self._filters)
    for filter in important_filters :
      filter.avs(self, vs)
    for v in vs :
      self._v.add(v)
  def ae(self, *e) :
    """
    Add an edge to the current ``DiGraph`` instance.  If only one argument is provided, it should be an edge.
    If multiple arguments are provided, they will be fed into an ``Edge`` constructor.
    """
    if len(e) == 1 :
      self.aes(e)
    else :
      self.aes(Edge(*e))
  def aes(self, *es) :
    """
    Add every edge in list of edges `es` to the current ``DiGraph`` instance.  The edges should be defined according to one of the conventions in the ``ae`` docstring.
    
    For example ::
    
      >>> from organdiae import *
      >>> g = DiGraph()
      >>> g.avs([ng('foo', name=True),ng('bar', name=True), ng('mike', name=True)])
      >>> g.aes([[foo,bar],Edge(foo,mike)])
      >>> g.p()
      VERTICES
          0. foo
          1. bar
          2. mike
      EDGES
          0. foo --> bar
          1. foo --> mike
    """
    es = list(es)
    important_filters = Filter.find_minimum_filter_list(self._filters)
    for x in range(len(es)) :
      if (type(es[x]) == type(())) | (type(es[x]) == type([])) :
        es[x] = Edge(*tuple(es[x]))
    for filter in important_filters :
      filter.aes(self, es)
    for e in es :
      self._e.add(e)
      self._v.add(e._v1)
      self._v.add(e._v2)
      if not self._v1.has_key(e._v1) :
        self._v1[e._v1] = []
      self._v1[e._v1].append(e)
      if not self._v2.has_key(e._v2) :
        self._v2[e._v2] = []
      self._v2[e._v2].append(e)
  def rv(self, v) :
    """Remove vertex `v` from current ``DiGraph`` instance."""
    self.rvs(v)
  def rvs(self, *vs) :
    """Remove all vertices in `vs` from current ``DiGraph`` instance."""
    vs = list(vs)
    for v in vs :
      if v not in self._v :
        raise RemoveError('Vertex already in system, cannot add.')
    important_filters = Filter.find_minimum_filter_list(self._filters)
    for filter in important_filters :
      filter.rvs(self, vs)
    for v in vs :
      self._v.remove(v)
      offenders = []
      try : 
        offenders += self._v1[v]
        for e in self._v1[v] :
          self._v2[e._v2].remove(e)
        del self._v1[v]
      except KeyError : pass
      try : 
        offenders += self._v2[v]
        for e in self._v2[v] :
          self._v1[e._v1].remove(e)
        del self._v2[v]
      except KeyError : pass
      for edge in offenders : self._e.remove(edge)
  def re(self, e) :
    """Remove edge `e` from current ``DiGraph`` instance."""
    self.res(e)
  def res(self, *es) :
    """Remove all edges in `es` from current ``DiGraph`` instance."""
    es = list(es)
    important_filters = Filter.find_minimum_filter_list(self._filters)
    for filter in important_filters :
      filter.aes(self, es)
    for e in es :
      self._e.remove(e)
      self._v1[e._v1].remove(e)
      if self._v1[e._v1] == [] : del self._v1[e._v1]
      self._v2[e._v2].remove(e)
      if self._v2[e._v2] == [] : del self._v2[e._v2]
  def normalizeEdges(self) :
    """
    Debugging method - if you tinker with ``self._e`` or ``self._v`` accidentally, run this to make sure all is correctly represented in the graph.
    """
    self._v1 = {}
    self._v2 = {}
    for v in self._v :
      if isinstance(v,DiGraph) : v.normalizeEdges()
    for e in self._e :
      if not self._v1.has_key(e._v1) : self._v1[e._v1] = []
      self._v1[e._v1].append(e)
      if not self._v2.has_key(e._v2) : self._v2[e._v2] = []
      self._v2[e._v2].append(e)
  @staticmethod
  def toGraphViz(digraph, path, nested=True, create=True, labeling_scheme = None, program='dot', depth=0) :
    """
    Exports a current graph to `path`, invoking graphViz if `create=True` and using labeling scheme `labeling_scheme` to label the edges.
    The normal bootstrap identifies a simple and effective labeling scheme.
    
    .. todo::
    
      Make this more modular (ie extend the labeling scheme paradigm to vertices and even the graph on the whole).
    """
    if not which(program) :
      return OSError('It looks like '+program+' is not in your search path.\nFix and try again.')
    short_path = path.split('/')[-1]
    if not labeling_scheme :
      labeling_scheme = lambda x : ''
    url = ''
    if nested :
      try : shutil.rmtree(path)
      except Exception, e : pass
      os.makedirs(path)
      path = os.path.join(path,short_path)
      url = '\tURL="'+short_path+'.svg";\n'
    outfi_l = []
    outfi_l.append('digraph '+digraph.__name__+' {\n'+url+'\tcenter=true;\n\toverlap=false;\n')
    for v in digraph._v :
      url = ''
      if os.path.exists(str(v.ilsagitde)) :
        if os.path.isabs(str(v.ilsagitde)) :
          gp = 'file://'+str(v.ilsagitde)
        else :
          gp = os.path.normpath(((depth+1)*'../')+v.ilsagitde)
        url = ',URL="'+gp+'",style="filled",fillcolor=green'
      # Note : when there is a conflict between a file and a subgraph (which is conceptually bizarre and should never happen), Organdiae chooses the subgraph
      if nested :
        if isinstance(v, DiGraph) :
          if len(v._v) > 0 :
            url = ',URL="'+v.__name__+'/'+v.__name__+'.svg",style="filled",fillcolor=red'
            DiGraph.toGraphViz(v,os.path.join(path.rpartition('/')[0],v.__name__),nested=nested,create=create,labeling_scheme=labeling_scheme,program=program,depth=depth+1)
      isd = str(v.ilsagitde)
      if os.path.isabs(str(v.ilsagitde)) : isd = str(v.ilsagitde).split('/')[-1]
      outfi_l.append('\t'+v.__name__+' [label="'+isd+'"'+url+'];\n')
    for e in digraph._e : 
      outfi_l.append('\t'+e._v1.__name__+' -> '+e._v2.__name__+' [dir=forward'+labeling_scheme(e)+'];\n')
    outfi_l.append('}\n')
    outfi = file(path+'.dot','w')
    for line in outfi_l : outfi.write(line)
    outfi.close()
    if create :
      if not which(program) :
        return OSError('It looks like '+program+' is not in your search path.\nFix and try again.')
      if nested : 
        subprocess.call(program+' -Tsvg -o'+path+'.svg '+path+'.dot', shell=True)
      else : subprocess.call(program+' -Tgif -o'+path+'.gif '+path+'.dot', shell=True)
      
class Filter(_OrgandiaeObject) :
  """
  Base class for all filters.  Currently, Vertex, Edgeless, Tree, and Forest derive from it.
    
  Every filter must define 8 methods that either return ``True`` or raise an ``OrgandiaeError`` depending on if a request is permissible or not given what the filter does.
  These methods are: ``av``, ``avs``, ``ae``, ``aes``, ``rv``, ``rvs``, ``re``, ``res``.  For more information on what these methods are, consult the documentation for DiGraph.
  """
  @staticmethod
  def find_minimum_filter_list(filters) :
    filters = set(filters)
    offenders = []
    for x in range(len(filters)-1) :
      for y in range(x,len(filters)) :
        if issubclass(filters[x],filters[y]) : offenders.append(filters[y])
        if issubclass(filters[y],filters[x]) : offenders.append(filters[x])
    return list(filters.difference(set(offenders)))
  @staticmethod
  def is_a(digraph) : 
    """
    Checks to see if the graph could have been grown entirely under this filter.
    For example, if ran with Forest, this would answer the question "Is this graph a forest?"
    """
    pass
  @staticmethod
  def av(digraph, v) : pass
  @staticmethod
  def avs(digraph, vs) : pass
  @staticmethod
  def ae(digraph, e) : pass
  @staticmethod
  def aes(digraph, es) : pass
  @staticmethod
  def rv(digraph, v) : pass
  @staticmethod
  def rvs(digraph, vs) : pass
  @staticmethod
  def re(digraph, e) : pass
  @staticmethod
  def res(digraph, es) : pass

class Vertex(Filter) :
  """Filter that rejects all addition statements."""
  @staticmethod
  def is_a(digraph) : 
    if len(digraph._v) > 0 : raise OrgandiaeError
    return True
  @staticmethod
  def av(digraph, v) : raise OrgandiaeError('Cannot add elements to a vertex.')
  @staticmethod
  def avs(digraph, vs) : raise OrgandiaeError('Cannot add elements to a vertex.')
  @staticmethod
  def ae(digraph, e) : raise OrgandiaeError('Cannot add elements to a vertex.')
  @staticmethod
  def aes(digraph, es) : raise OrgandiaeError('Cannot add elements to a vertex.')
  @staticmethod
  def rv(digraph, v) : return True
  @staticmethod
  def rvs(digraph, vs) : return True
  @staticmethod
  def re(digraph, e) : return True
  @staticmethod
  def res(digraph, es) : return True

class Edgeless(Filter) :
  """Filter that rejects all addition of edges."""
  @staticmethod
  def is_a(digraph) : 
    if len(digraph._e) > 0 : raise OrgandiaeError
    return True
  @staticmethod
  def av(digraph, v) : return True
  @staticmethod
  def avs(digraph, vs) : return True
  @staticmethod
  def ae(digraph, e) : raise OrgandiaeError('Cannot add edges to an edgeless graph.')
  @staticmethod
  def aes(digraph, es) : raise OrgandiaeError('Cannot add edges to an edgeless graph.')
  @staticmethod
  def rv(digraph, v) : return True
  @staticmethod
  def rvs(digraph, vs) : return True
  @staticmethod
  def re(digraph, e) : return True
  @staticmethod
  def res(digraph, es) : return True

class Forest(Filter) :
  """Filter that rejects all simple loops."""
  @staticmethod
  def is_a(digraph) : 
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    if len(v1keys) > len(v2keys) : return False
    heads = set(v1keys).difference(set(v2keys))
    def crawl(head, digraph=digraph, garbage=[]) :
      garbage.append(head)
      if digraph._v1.has_key(head) :
        for edge in digraph._v1[head] :
          if edge._v2 in garbage : raise OrgandiaeError
          crawl(edge._v2, digraph, garbage)
    for head in heads :
      crawl(head)
    return True    
  @staticmethod
  def av(digraph, v) : return True
  @staticmethod
  def avs(digraph, vs) : return True
  @staticmethod
  def ae(digraph, e) : 
    Forest.aes(digraph, [e])
  @staticmethod
  def aes(digraph, es) : 
    if (len(digraph._v) == 0) & (len(es) == 1) : return True
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    for e in es :
      v1keys.append(e._v1)
      v2keys.append(e._v2)
    sv2keys = set(v2keys)
    # Make sure that we're not doubling up on v2s
    if len(v2keys) > len(sv2keys) : raise OrgandiaeError('Error adding edge to a forest.')
    for e in es :    
      # Check to see this is not adding any backward paths
      if (e._v1 in v2keys) & (e._v2 in v1keys) : raise OrgandiaeError('Error adding edge to a forest.')
    return True
  @staticmethod
  def rv(digraph, v) : return True
  @staticmethod
  def rvs(digraph, vs) : return True
  @staticmethod
  def re(digraph, e) : return True
  @staticmethod
  def res(digraph, es) : return True
    
class Tree(Forest) :
  """Filter that rejects all simple loops and all moves that move away from 1-connectivity."""
  @staticmethod
  def is_a(digraph) : 
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    heads = set(v1keys).difference(set(v2keys))
    if len(heads) != 1 : raise OrgandiaeError
    if digraph._v != set(v1keys).union(set(v2keys)) : raise OrgandiaeError
    def crawl(head, digraph=digraph, garbage=[]) :
      garbage.append(head)
      if digraph._v1.has_key(head) :
        for edge in digraph._v1[head] :
          if edge._v2 in garbage : raise OrgandiaeError
          crawl(edge._v2, digraph, garbage)
    for head in heads :
      crawl(head)
    return True    
  @staticmethod
  def av(digraph, v) :
    Tree.avs(digraph, [v])
  @staticmethod
  def avs(digraph, vs) :
    if len(digraph._v) > 0 : raise OrgandiaeError('Error adding vertex to a tree.')
    if len(vs) > 1 : raise OrgandiaeError('Error adding vertex to a tree')
    return True
  @staticmethod
  def ae(digraph, e) : 
    Tree.aes(digraph, [e])
  @staticmethod
  def aes(digraph, es) :
    if (len(digraph._v) == 0) & (len(es) == 1) : return True
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    oldlen = len(set(v1keys).difference(set(v2keys)))
    for e in es :
      v1keys.append(e._v1)
      v2keys.append(e._v2)
    # Make sure we haven't added any heads
    sv1keys = set(v1keys)
    sv2keys = set(v2keys)
    if (oldlen == 0) :
      if (len(sv1keys.difference(sv2keys)) != 1) : raise OrgandiaeError('Error adding edges to a tree.')
    elif len(sv1keys.difference(sv2keys)) > oldlen  : raise OrgandiaeError('Error adding edges to a tree.')
    # Make sure that we're not doubling up on v2s
    if len(v2keys) > len(sv2keys) : raise OrgandiaeError
    for e in es :    
      # Check to see this is not adding any backward paths
      if (e._v1 in v2keys) & (e._v2 in v1keys) : raise OrgandiaeError('Error adding edges to a tree.')
    return True
  @staticmethod
  def rv(digraph, v) : 
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    tail = set(v2keys).difference(set(v1keys))
    head = set(v1keys).difference(set(v2keys))
    if v in tail : return True
    if (v in head) & (len(digraph.v1[v]) == 1) : return True
    raise OrgandiaeError
  @staticmethod
  def rvs(digraph, vs) :
    v1keys = digraph._v1.keys()
    v2keys = digraph._v2.keys()
    tail = set(v2keys).difference(set(v1keys))
    head = set(v1keys).difference(set(v2keys))
    changed = True
    while changed :
      changed = False
      for v in vs :
        if (v in head) & (len(digraph.v1[v]) == 1) :
          changed = True
          head.remove(v)
          vs.remove(v)
          break
        elif v in head : raise OrgandiaeError
    for v in vs :
      if v not in tail : raise OrgandiaeError
    return True
  @staticmethod
  def re(digraph, e) : raise OrgandiaeError
  @staticmethod
  def res(digraph, es) : raise OrgandiaeError

class Crawler(object) :
  """
  Effectuates traversals (crawls) of a ``DiGraph`` instance.
  This is done through two main methods, neither of which have a docstring, both of which are described here.
  
  * ``crawl_with_subgraphs`` crawls through a ``DiGraph`` instance recursively (ie touching upon all nodes that are also instances of DiGraph).
  * ``crawl_without_subgraphs`` crawls through a ``DiGraph`` without crawling through pertinant subgraphs.

  The arguments to both of these methods are:
  
  `gl`
    A list of graphs to crawl.
  `vl`
    A list of lists of vertices.  Each list corresponds to a graph in ``gl``.  Each vertex in each list is a point to start the crawl from.  The algorithm is greedy, so it will crawl maximally with the first vertex, then move on to the second, etc.  Useful when crawling through structures where buses depend on the reults of other buses to effectuate certain calculations.
  `pl`
    A list of lists of buses.  Each list gorresponds to a graph in ``gl``.  Each bus in each list is a bus to traverse.  Again, this is greedy.
  `il`
    A list of lists of initial values.  That is, because the crawls operate by convolution, we need a first value to convolve from.  Often, this is simply a unit impulse.
  
  See the tutorial on crawling for a detailed example of how the crawler works.
  """
  @staticmethod
  def crawl_with_subgraphs(gl, vl, pl, il) :
    Crawler.crawl(gl, vl, pl, il, True)
  @staticmethod
  def crawl_without_subgraphs(gl, vl, pl, il) :
    Crawler.crawl(gl, vl, pl, il, False)
  """
  graphList, vertexLists(!), pathLists(!), initialValueLists(!)
  """
  @staticmethod
  def crawl(gl, vl, pl, il, subgraphs) :
    # Check that everything passed in is the same length...otherwise, broken!
    if len(set([len(vl), len(gl), len(pl), len(il)])) != 1 : raise OrgandiaeError
    oldlen = 0
    newlen = len(vl)
    while oldlen != newlen :
      for x in range(len(vl)) :
        if vl[x] == [] : gl[x] = list(gl[x])
        if pl[x] == [] : pl[x] = vl[x]._f.keys()
        if il[x] == [] :
          for x in len(range(pl)) :
            il.append(pl[x].return_type())
        # NEED TO CHECK INIT VALS!!!
        if subgraphs :
          if isinstance(vl[x], DiGraph) : 
            gl.append(vl[x])
            gl.append(list(vl[x]._v))
            pl.append(list(pl[x]))
            #WRONG! FIX THIS SHIT! ADD CORRECT INITIALS!!!!!!!!!
            #il.append(list(il[x]))
      oldlen = newlen
      newlen = len(vl)
    # Reset the bad stuff
    for x in range(len(gl)) :
      graph = gl[x]
      for edge in graph._e :
        for p in pl[x] :
          try : edge._cf[p].reset()
          except Exception, e : 
            print "May not work as expected due to incomplete path, more specifically..."
            print e
    oldlen = -1
    newlen = 0
    garbage = []
    # Make the crawl engine mark!
    while newlen != oldlen :
      # Internalize path list!!!!!  Cannot have it in crawl engine...doesn't make sense...
      for x in range(len(gl)) :
        for y in range(len(pl[x])) :
          Crawler.__crawl_engine(gl[x],vl[x],pl[x][y],il[x][y], garbage)
      oldlen = newlen
      newlen = len(garbage)
  @staticmethod
  def __crawl_engine(g, v, p, i, garbage) :
    # Check to see if g._v contains anything that falls outside of the group!
    if set(v).union(set(g._v)) != set(g._v) :
      print "Vertex problem...fixing...but you may get undesirable results!"
      v = set(v).intersection(set(g._v))
    to_ex = []
    for x in range(len(v)) :
      if not g._v1.has_key(v[x]) : continue
      for edge in g._v1[v[x]] :
        # For every v in vertex list, for every edge w/ this as v1, if edge not in garbage, do the function, add the edge, crawl more
        if (edge, p) not in garbage :
          try :
            edge._cf[p].initialize(edge._f[p](i))
            garbage.append((edge,p))
            to_ex.append((g, [edge._v2], p, edge._cf[p], garbage))
          except NotEnoughInfoError, e : pass
    for ex in to_ex :
      Crawler.__crawl_engine(*ex)

def ng(isd, dg=DiGraph, name=None, **kwargs) :
  """
  Use this to create all subclasses of DiGraph that you care to keep (ie those you use in graphs) should be created through this function.
  
  Arguments:
  
  `isd`
    ``ilsagitde`` for the digraph.
  `dg`
    ``DiGraph`` from which this new digraph will inherit.
  `name`
    `True` if a ``DiGraph`` with name ``isd`` should be added to the ``__main__`` namespace.
  `kwargs`
    Will be the dictionary of the new ``DiGraph`` subclass.
  """
  if not issubclass(dg, DiGraph) : raise OrgandiaeError('Named digraphs must subclass digraph!!!')
  kwargs['ilsagitde'] = isd
  if not name :
    name = _randString()
  elif name == True :
    name = isd
  newdg = type(name, (dg,), kwargs)
  setattr(sys.modules['__main__'], name, newdg)
  globals()[name] = newdg
  CLASS_HEIRARCHY.append((isd, name, dg.__name__, kwargs))
  return newdg