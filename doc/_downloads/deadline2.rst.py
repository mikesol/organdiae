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

