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

pdf = polyu.bpcd((0,0),(1,20.,1),(1,0,0),(7,1,1),(2.5,3,1),(2.5,0,0),pw=3).normalizeIntegral()
def silence_sound() :
	b = rand_collect_length(9., lambda out, x : pdf.g0integrator(x,n=True), i=False)
	for x in range(len(b)) : print "SILENCE" if not x%2 else "SOUND", b[x]
	return b

recolte=silence_sound()
recolte=silence_sound()
recolte=silence_sound()
recolte=silence_sound()
g.av(ng('silence',name=True))
g.av(ng('sound', name=True))
su = ng('structural unit')
g.ae(silence,trio,sb(su))
g.ae(sound,trio,sb(su))
ng('order', name=True)
realdeal = order()
siso = [sound(recolte[x]) if x%2 else silence(recolte[x]) for x in range(len(recolte))]
ng('follows', name=True)
realdeal.av(siso[0])
for x in range(1,len(siso)) : realdeal.ae(siso[x-1],siso[x],sb(follows))
g.av(realdeal)
pick() # Never forget to save!
simat = [ng(x) for x in ['bowing body of instrument', 'lightly tapping on instrument', 'above the bridge pizz']]
sigraph = DiGraph('silence materials')
for x in simat : sigraph.av(x)
g.av(sigraph)
def gimme_silence(b,sil) :
	out = [(random.choice(sil), b[x]) for x in range(len(b)) if not x%2]
	for x in out : print x[0].ilsagitde, x[1]
	return out

sitypes = gimme_silence(recolte,simat)
sitypes = gimme_silence(recolte,simat)
sitypes = gimme_silence(recolte,simat)
genre = ng('genre')
for x in range(len(siso)) :
	if not x%2 : realdeal.ae(siso[x], sitypes[x/2][0], sb(genre))

pick()
gv(g, path='enfin')
