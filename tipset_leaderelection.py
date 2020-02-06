import networkx as nx
import numpy as np 
import itertools

sim=200 #number of simulations
nh=67 #number of honest players
na=33#number of adversarial players
ntot=na+nh #total num,ber of players
p=1./float(ntot) #proba for one leader to be elected
Kmax=40 #length of the attack
grind_max=30 #how many "grinds" we allow

print("With Kmax = {k} and grind_max = {g}, we have: ".format(k=Kmax,g=grind_max))

### How many times does the adversary have a longest chain than honest chain with 33% of power?


### Grinding:
def grind(n):
	index_parent = n
	wght = G.node[n]['weight']
	c = G.node[n]['num_winner']
	slot = G.node[n]['slot']
	global ct
	global current_list
	if slot<Kmax:
		for i in range(grind_max):
			j=slot+i+1
			for k in range(c):
				ca = np.random.binomial(na, p, 1)[0]
				if ca>0 and j<Kmax:
					ct+=1
					G.add_node(ct,slot=j,weight=wght+k+1,num_winner=ca,parent=n)##add all the blocks
					#I can include
					G.add_edge(index_parent,ct)
					current_list.append(ct)#add all new nodes to the list
			#if no leader we need to go direct to the delay case 
		#remove n from list
	current_list.remove(n)

##adversarial fork without grinding:
forks=[]
for i in range(sim):
	nogrinding_fork_weight=0
	slot_number=0
	ca = np.random.binomial(na, p, 1)[0]#honest players each toss a coin to see if elected leaders
	while slot_number<Kmax:
		nogrinding_fork_weight+=ca
			#no leaders elected everyone moves to next slot
		slot_number+=1
		ca = np.random.binomial(na, p, 1)[0]#each honest leaders toss
			#a new coin for that round
	forks.append(nogrinding_fork_weight)


print "Weight of Fork without grinding (adversary): {f}.".format(f=np.average(forks))

forks_adv=[]
for i in range(sim):
	G=nx.DiGraph()
	G.add_node(0,slot=0,weight=0,num_winner=1)
	ct=0
	current_list=[0]
	max_w=0
	while current_list :
		for n in current_list:
			#print(current_list)
			if G.node[n]['weight']>max_w: max_w = G.node[n]['weight']
			grind(n)
	forks_adv.append(max_w)
print "Weight of adversarial fork with grinding: {f}".format(f=np.average(forks_adv))

#what happens to the rest of the player?
forks_honest=[]
for i in range(sim):
	honest_fork_weight=0
	slot_number=0
	ch = np.random.binomial(nh, p, 1)[0]
	while slot_number<Kmax:
		#there were leaders elected, one block is created
		honest_fork_weight+=ch
			#no leaders elected everyone moves to next slot
		slot_number+=1
		ch = np.random.binomial(nh, p, 1)[0]#each honest leaders toss
			#a new coin for that round
	forks_honest.append(honest_fork_weight)

print "Weight of fork for the rest of player: {f}.".format(f=np.average(forks_honest))


quality=[1 if forks_adv[i]>=forks_honest[i] else 0 for i in range(sim)  ]
#praosh=[1 for i in range(len(ch)) if ch[i]>0 ]

#longest chain case:
print "Adversary wins with probability: {f}. \nWithout grinding \
the adversary wins with probability: {f2}".format(f=np.average(quality),\
	f2=np.average([1 if forks[i]>=forks_honest[i] else 0 for i in range(sim)  ]))