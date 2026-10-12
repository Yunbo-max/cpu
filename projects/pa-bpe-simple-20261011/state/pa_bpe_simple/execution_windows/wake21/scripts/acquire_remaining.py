import runpy, sys
for index in range(1,6):
    sys.argv=['scripts/acquire_source.py',str(index)]
    runpy.run_path('scripts/acquire_source.py',run_name='__main__')
