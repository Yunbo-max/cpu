#!/usr/bin/env python3
"""Synthetic toy: outage incidence versus periodic observation. NO actual NYISO rows."""
import json,math,time
def main():
    started=time.process_time()
    events={"A":1,"B":100};dur_min={"A":1440,"B":5};snapshot={k:events[k]*dur_min[k]//5 for k in events}
    pe={k:events[k]/sum(events.values()) for k in events}
    ps={k:snapshot[k]/sum(snapshot.values()) for k in events}
    a=max(ps,key=ps.get);b=max(pe,key=pe.get)
    risk=lambda selected,p:(1-p[selected])/2
    ratio=risk(a,pe)/risk(b,pe)
    assert a=="A" and b=="B" and math.isclose(ratio,100,rel_tol=1e-12)
    print(json.dumps({"events":events,"duration_minutes":dur_min,"snapshot_rows":snapshot,
      "incident_probs":pe,"snapshot_probs":ps,"snapshot_choice":a,"event_choice":b,
      "incident_error_snapshot_choice":risk(a,pe),"incident_error_incident_choice":risk(b,pe),
      "error_ratio":ratio,"cpu_process_seconds":time.process_time()-started},indent=2))
if __name__=="__main__":main()
