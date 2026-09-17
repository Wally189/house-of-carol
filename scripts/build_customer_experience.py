from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_case_studies.py')], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'customer_experience_transform.py')], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'customer_experience_finish.py')], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'editorial_remediation_finalize.py')], cwd=ROOT, check=True)
print('PASS: canonical commercial build completed and customer-experience layer applied')
