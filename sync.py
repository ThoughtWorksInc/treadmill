import subprocess
import sys

branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
branch_name = branch_name.strip() + '-merge'
subprocess.call(['git', 'branch', '-D', branch_name])
subprocess.call(['git', 'pull', '--rebase'])
subprocess.call(['git', 'checkout', '-b', branch_name])
terminal_commit = sys.argv[1]
subprocess.call(['git', 'reset', '--soft', terminal_commit])
subprocess.call(['git', 'commit', '--amend', '--no-edit'])
subprocess.call(['git', 'push', 'origin', branch_name])
