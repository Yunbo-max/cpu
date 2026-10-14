def classify(status,launch,raw,guard_rc,guard_status):
 launched=bool(launch and launch.get('native_Popen_returned')) or status is not None or ('done reading input!' in raw and 'Start building abstraction.' in raw)
 if guard_rc==0:outcome='solved'
 elif guard_status in ['process_group_rss_guard','shared_cgroup_memory_guard','timeout']:outcome='outer_resource_censored'
 elif status and status['native_process_returncode']==22:outcome='native_memory_censored'
 elif status and status['native_process_returncode'] in [23,-24]:outcome='native_CPU_time_censored'
 else:outcome='other_failure_requires_diagnosis'
 return {'native_launched':launched,'outcome':outcome,'valid_observation':guard_rc==0 or outcome in ['native_memory_censored','native_CPU_time_censored'],'native_CPU_accounting_complete':bool(status and 'native_reaped_child_cpu_seconds' in status)}
