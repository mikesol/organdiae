


from organdiae import *
bs('declaration')
words = 'he sells sea shells by the sea shore'.split(' ')
g = DiGraph()
for word in set(words) :
	g.av(ng(word, name=True))

follows = ng('follows')
for x in range(len(words)-1) :
	g.ae(globals()[words[x]], globals()[words[x+1]], sb(follows))	

gv(g, path='words', program='dot')
h = DiGraph()
h.avs(ng('state1', name=True),ng('state2', name=True),ng('state3', name=True),ng('state4',name=True))
weighted = ng('weighted connection')
e1 = Edge(state1, state2, sb(weighted))
e2 = Edge(state1, state3, sb(weighted))
e3 = Edge(state2, state4, sb(weighted))
h.aes(e1, e2, e3)
Weight = ng('Weight', return_type=PP)
fstr = ['a = (args[0].deltaFunction().convolve(args[1].deltaFunction())).piecewisePolynomial()','a']
h.p()
h.g(1,0).ab(Weight, CF(fstrings=fstr,args=(PP([P((0.5,0.125)),P((0.,1.))],[-4.,0.,1.],[I(1.0)],[0.]),)))
h.g(1,1).ab(Weight, CF(fstrings=fstr,args=(PP([P((-1.,1.)),P((3.,-1.))],[1.,2.,3.],[],[]),)))
h.g(1,2).ab(Weight, CF(fstrings=fstr,args=(PP([P((1.,-1./3)),P((-3.,1.))],[0.,3.,4.],[],[]),)))
gv(h, path='states', program='dot')
Crawler.crawl_with_subgraphs([h],[[h.g(0,0)]],[[Weight]],[[PP([],[],[I(1.)],[0.])]])
for edge in [e1,e2,e3] :
	edge._cf[Weight].toGNUPlot(edge._v2.ilsagitde+'.gnu')

pick()
