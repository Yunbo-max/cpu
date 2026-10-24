#!/usr/bin/env python3
import math
for delta in [0.2,0.8,1.2]:
    r=1.
    proxy=(max(0,r-delta),max(0,delta-r))
    robust=(max(0,r*math.sqrt(2)-delta),delta+r*math.sqrt(2))
    print(delta,proxy,robust)
