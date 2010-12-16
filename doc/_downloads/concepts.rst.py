
from organdiae import *
bs('sixConcepts')
jar = ng('jar')
pot = ng('pot')
brick = ng('brick')
g = DiGraph()
g.av(jar)
g.av(pot)
g.av(brick)
type(jar)
issubclass(jar,DiGraph)

g.p()

DiGraph.toGraphViz(g, 'ex1')

jar1 = jar()
jar2 = jar()
pot1 = pot()
for item in [jar1, jar2, pot1] :              
	for x in range(2) :
		item.av(brick())
	g.av(item)

g.p()

DiGraph.toGraphViz(g, 'ex2')

forest = DiGraph(filters=[Forest])
for x in ['abraham','isaac','jacob','esau','joseph','benjamin','father'] :
    dummy = ng(x, name=True)

abraham
for x in [abraham,isaac,jacob,esau,joseph,benjamin] :
    forest.av(x)

forest.ae(abraham,isaac,sb(father))
forest.ae(isaac,jacob,sb(father))
forest.ae(isaac,esau,sb(father))
forest.ae(jacob,joseph,sb(father))
forest.ae(jacob,benjamin,sb(father))
forest.p()
try : forest.ae(isaac, abraham, sb(father))
except OrgandiaeError, e : print e

DiGraph.toGraphViz(forest, 'bible', program='dot')

newbrick = brick(filters=[Vertex])
hole = ng('hole')
try : newbrick.av(hole)
except OrgandiaeError, e : print e


ng('inside', name=True)
newbrick.df(Vertex)
newbrick.af(Edgeless)
holes = []
for x in range(3) : 
    holes.append(hole())
    newbrick.av(holes[-1])

newbrick.p()
try : newbrick.ae(holes[0], holes[1], sb(inside))
except OrgandiaeError, e : print e


jupiter = ng('jupiter')
planets = ng('the planets')
movement = ng('movement')
holst = DiGraph()
holst.ae(jupiter,planets,sb(movement))

holst.p()

gv(holst, path='holst1')

mars = ng('the planets')
holst.ae(mars,planets,sb())
gv(holst, path='holst2')

soundFetishGroup = ng('sound fetish group')
yngwie = ng('Yngwie Malmsteen solo')
chalk = ng('nails on chalkboard')
sfg1 = soundFetishGroup()
sfg1.av(yngwie)
sfg1.av(chalk)
guiltyPleasures = DiGraph()
guiltyPleasures.av(sfg1)

flam = ng('flam')
paradiddle = ng('single paradiddle')
drag = ng('single drag')
ruff = ng('ruff')
ratamacue = ng('single ratamacue')
ng('temporalGap', name=True, return_type = PiecewisePolynomial)
follows = ng('follows')
rudiments = DiGraph(filters=[Tree])
finalruff = ruff()
tree_order = [flam(),[drag(),ruff(),[ratamacue(), paradiddle(), [paradiddle()], flam(), [ratamacue(), drag(), [flam(), [ratamacue(), drag(), [finalruff]]]]]]]
def make_tree(graph, order, v=None) :
	for x in range(len(order)) :
		if type(order[x]) != type([]) :
			if v == None : graph.av(order[x])
			else : graph.ae(v, order[x], sb(follows, nbuses=['temporalGap']))
		else :
			make_tree(graph, order[x], order[x-1])

make_tree(rudiments, tree_order)
rudiments.p()
gv(rudiments, path='rudiments', program='dot')

for e in rudiments._e :
	if isinstance(e._v1,flam) & isinstance(e._v2,drag) :
		e._f[temporalGap].args = (PiecewisePolynomial([Polynomial((0.,1./3)), Polynomial((2., -1.)),Polynomial((-1.,1./2)),Polynomial((2.,-1./2))],[0.0,1.5,2.0,3.0,4.0],[],[]),)
	else :
		e._f[temporalGap].args = (PiecewisePolynomial([Polynomial((1.5,-1./2))],[1.0,3.0],[],[]),)


Crawler.crawl_with_subgraphs([rudiments], [[tree_order[0]]], [[temporalGap]], [[PiecewisePolynomial([],[],[Impulse(1.0)],[0.])]])

for e in rudiments._e :
	if e._v2 == finalruff :
		e._cf[temporalGap].toGNUPlot('finalRuff1.gnu')
		break


Crawler.crawl_with_subgraphs([rudiments], [[tree_order[1][2][3]]], [[temporalGap]], [[PiecewisePolynomial([],[],[Impulse(1.0)],[0.])]])

for e in rudiments._e :
	if e._v2 == finalruff :
		e._cf[temporalGap].toGNUPlot('finalRuff2.gnu')
		break


pick()

gkeys = globals().keys()
untouchable = ['__builtins__', '__name__', '__doc__', '__package__']
for key in gkeys :
	if key not in untouchable : del globals()[key]

from sixConcepts import *
rudiments.p()

instrument = ng('instrument')
theremin = ng('theremin', instrument, age=88)
issubclass(theremin, instrument)
theremin.age
