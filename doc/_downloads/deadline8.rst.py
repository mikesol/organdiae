from organdiae import *
bs('trio')
g = DiGraph()
for x in ['violin','viola','cello', 'plays','trio'] :
	ng(x, name=True)

g.ae(violin,trio,sb(plays))
g.ae(viola,trio,sb(plays))
g.ae(cello,trio,sb(plays))
gv(g,path='ratherLimited')
booty = DiGraph('sonic plunder')
for x in os.walk('pillage') :
	for y in x[2] :
		booty.av(ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y)))))

booty.p()
g.av(booty)
em = DiGraph('emilie lesbros sounds')
for x in os.walk('emilie') :
	for y in x[2] :
		em.av(ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y)))))

em.p()
g.av(em)
scdict = {}
scsess = DiGraph('supercollider goodness')
for x in os.walk('scdocs') :
	for y in x[2] :
		scdict[y] = ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y))))
		scsess.av(scdict[y])


example = ng('example')
for x in os.walk('scbounces') :
	for y in x[2] :
		fileg = ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y))))
		scsess.ae(fileg, scdict[y.rpartition('.')[0].rpartition('.')[0]], sb(example))

g.av(scsess)
cues = DiGraph('cues')
for x in os.walk('cues') :
	for y in x[2] :
		cues.av(ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y)))))

cues.p()
g.av(cues)
scans = DiGraph('scans')
for x in os.walk('scans') :
	for y in x[2] :
		scans.av(ng(os.path.normpath(os.path.join(os.getcwd(),os.path.join(x[0],y)))))

g.av(scans)
