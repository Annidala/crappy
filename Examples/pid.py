#coding: utf-8
from __future__ import print_function,division

import crappy

g = crappy.blocks.Generator([
  {'type':'ramp','speed':100,'condition':'delay=10'},
  {'type':'constant','value':1800,'condition':'delay=10'},
  {'type':'constant','value':500,'condition':'delay=10'},
  {'type':'sine','amplitude':2000,'offset':1000,'freq':.3,'condition':'delay=15'}
  ])

kv = 1000

mot = crappy.blocks.Machine([{'type':'Fake_motor',
                             'cmd':'pid',
                             'mode':'speed',
                             'speed_label':'speed',
                             # Motor properties:
                             'kv':kv,
                             'inertia':2,
                             'rv':.2,
                             'fv':1e-5
                             }])
graph_m = crappy.blocks.Grapher(('t(s)','speed'),('t(s)','cmd'))

crappy.link(mot,graph_m)
crappy.link(g,graph_m)
# To see what happens without PID
#crappy.link(g,mot)
#crappy.start()

p = 30/kv
i = 10/kv
d = .8/kv

pid = crappy.blocks.PID(kp=p,
                        ki=i,
                        kd=d,
                        out_max=10,
                        out_min=-10,
                        input_label='speed',
                        send_terms=True)

crappy.link(g,pid)
crappy.link(pid,mot)
crappy.link(mot,pid)
#crappy.link(mot,pid,condition=crappy.condition.Moving_avg(15))



graph_pid = crappy.blocks.Grapher(('t(s)','pid'))
crappy.link(pid,graph_pid)

graph_pid2 = crappy.blocks.Grapher(('t(s)','p_term'),
                                   ('t(s)','i_term'),
                                   ('t(s)','d_term'))

crappy.link(pid,graph_pid2)

#crappy.start(high_prio=True)
crappy.start()
