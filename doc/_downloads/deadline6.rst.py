from organdiae import *
bs('trio')
g = DiGraph()
for x in ['violin','viola','cello', 'plays','trio'] :
	ng(x, name=True)

g.ae(violin,trio,sb(plays))
g.ae(viola,trio,sb(plays))
g.ae(cello,trio,sb(plays))
gv(g,path='ratherLimited')
import random
def rand_collect_length(l, f = lambda out, x : x, i=True, overshoot=True) :
	out = []
	sum = 0.0
	while sum < l :
		v = f(out,random.random())
		if i : v = round(v)
		sum += v
		out.append(v)
	if not overshoot : out = out[:-1]
	return out

def rand_collect_times(t, f = lambda out, x : x, i=True) :
	out = []
	for x in range(t) :
		v = f(out,random.random())
		if i : v = round(v)
		out.append(v)
	return out

materials = DiGraph(ilsagitde='materials')
fx = ['col_legni', 'jete', 'harmonic', 'sul_pont', 'sotto_pizz', 'bartok_pizz', 'xp', 'silence'] 
for x in fx :
	ng(x, name=True)
	materials.av(globals()[x])

g.av(materials)
gv(g, path='trioMaterial')
def dist_maker(fx=fx) :
	out = {}
	dist = rand_collect_times(t=len(fx), i=False)
	for x in range(len(fx)) :
		out[fx[x]] = dist[x]
	for x in out : print x, out[x]
	return out

dist = dist_maker()
dist = dist_maker()
dist = dist_maker()
ng('fetish', name=True)
g.ae(harmonic, trio, sb(fetish))
gv(g, path='trioFetish')
def makeorder(d) :
	k = d.keys()
	knh = [x for x in k if x != 'harmonic']
	kh = [x for x in k if x == 'harmonic']
	random.shuffle(knh)
	k = kh + knh
	k = [(x, d[x]) for x in k]
	for item in k :
		print item
	return k

o = makeorder(dist)
o = makeorder(dist)
o = makeorder(dist)
o = makeorder(dist)
order = DiGraph('piece order')
follows = ng('follows')
dv = globals()[o[0][0]](o[0][1])
order.av(dv)
for x in range(1, len(o)) :
	nv = globals()[o[x][0]](o[x][1])
	order.ae(dv,nv,sb(follows))
	dv=nv

g.av(order)
pick()
