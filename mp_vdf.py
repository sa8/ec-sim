#!/usr/bin/env python3

import numpy as np 
import itertools,time
import multiprocessing as mp
import random

sim=100000 #number of simulations
nh=67 #number of honest players
na=33#number of adversarial players
ntot=na+nh #total num,ber of players
e=1
p=float(e)/float(ntot) #proba for one leader to be elected
Kmax=8 #length of the attack
grind_max=Kmax #how many "grinds" we allow
VDF=10
vdf=10

start_time = time.time()

print("Grinding with headstart and Kmax = {k}, p={p} and grind_max = {g}, we have: ".format(k=Kmax,p=p,g=grind_max))

def inc(ct):
    with ct.get_lock():
        ct.value += 1

def new_node(n,slot,weight,num_winner,parent=0):
    return {
        'n': n,
        'slot': slot,
        'weight':weight,
        'num_winner':num_winner,
        'parent':parent,
    }

def try_grind(j,base_weight,parent,num_try=na):
    ca = np.random.binomial(num_try,p,1)[0]
    if ca < 1:
        return None
    # weight + ca - k
    weight = base_weight + ca 
    ## random index node
    idx = random.randrange(2**30)
    nnode = new_node(idx,j,weight,ca,parent)
    return nnode


### How many times does the adversary have a longest chain than honest chain with 33% of power?

def pgrind(info,n_grind = grind_max,num_try=na):
    index_parent = info['n']
    wght = info['weight']
    c = info['num_winner']
    slot = info['slot']
    ret = []
    if slot >= Kmax:
        return []

    for i in range(n_grind+1):
        j = slot +i*VDF + i +1
        if j >= Kmax:
            continue

        for k in range(c):
            nnode = try_grind(j,wght-k,index_parent,num_try=num_try)
            if nnode is not None:
                ret.append(nnode)
    return ret

def psimulation():
    forks_adv=[]
    cpus = mp.cpu_count()
    print("Parallel grinding simulation with {} cores:".format(cpus))
    with mp.Pool(processes=cpus) as pool:
        # if sim starts getting really high, should put pool computation at this
        # stage
        for i in range(sim):
            if i % 5 == 0:
                print("\t- simulation {}/{} starting".format(i,sim))
            nnode=new_node(0,-1,0,1,parent=-1)
            max_w=0
            current_list=[]
            current_list.extend(pgrind(nnode,n_grind=1,num_try=ntot))
            while len(current_list) > 0:
                ## ... might be better doing it in one shot at the end?
                max_w = max(n['weight'] for n in current_list)
                res = pool.map(pgrind,current_list)
                # flatten out [[n1,n2],[n3,n4...]]
                current_list = [n for subn in res for n in subn if len(n) > 0]
            forks_adv.append(max_w)
    print("\t--> Weight of adversarial fork with grinding: {f}".format(f=np.average(forks_adv)))
    return forks_adv

            
##adversarial fork without grinding:
forks=[]
for i in range(sim):
    nogrinding_fork_weight=0
    slot_number=0
    ca = np.random.binomial(na, p, 1)[0]#honest players each toss a coin to see if elected leaders
    while slot_number<Kmax:
        
            #no leaders elected everyone moves to next slot
        if ca>0:
            slot_number+=1
            nogrinding_fork_weight+=ca
        else:
            slot_number+=1+vdf
        ca = np.random.binomial(na, p, 1)[0]#each honest leaders toss
            #a new coin for that round
    forks.append(nogrinding_fork_weight)

print("Weight of Fork without grinding (adversary): {f}.".format(f=np.average(forks)))

forks_adv=psimulation()

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
        if ch==0:
            slot_number+=vdf
        ch = np.random.binomial(nh, p, 1)[0]#each honest leaders toss
            #a new coin for that round
    forks_honest.append(honest_fork_weight)

print("Weight of fork for the rest of player: {f}.".format(f=np.average(forks_honest)))


quality=[1 if forks_adv[i]>=forks_honest[i] else 0 for i in range(sim)  ]
#praosh=[1 for i in range(len(ch)) if ch[i]>0 ]

#longest chain case:
print("Adversary wins with probability: {f}. \nWithout grinding \
the adversary wins with probability: {f2}".format(f=np.average(quality),\
    f2=np.average([1 if forks[i]>=forks_honest[i] else 0 for i in range(sim) ])))

print("--- %s seconds ---" % (time.time() - start_time))