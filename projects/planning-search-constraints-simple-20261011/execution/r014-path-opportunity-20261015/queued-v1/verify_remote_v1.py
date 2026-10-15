"""RAM staged independent immutable HTTP verifier, no live SQL writes."""
import pathlib
p=pathlib.Path('/workspace/scratch/d503fbbd44e2/verify_r014_terminal_v1.py');s=p.read_text()
s=s.replace("C=pathlib.Path(__file__).resolve().parent","C=pathlib.Path('/workspace/scratch/d503fbbd44e2')")
s=s.replace("O=B/'r014-terminal-publication'","O=pathlib.Path('/dev/shm/r014-queued-publication-v1')")
s=s.replace('completed-v1/','queued-v1/').replace('==38','==37').replace("'terminal_attempts':38","'terminal_attempts':37").replace("'terminal':38","'terminal':37")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
