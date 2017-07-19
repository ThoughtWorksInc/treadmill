import subprocess
import sys

branch = sys.argv[1]
merge_branch = branch.strip() + '-merge'
subprocess.call(['git', 'checkout', branch])
subprocess.call(['git', 'branch', '-D', merge_branch])
subprocess.call(['git', 'pull', '--rebase'])
subprocess.call(['git', 'checkout', '-b', merge_branch])
terminal_commit = sys.argv[2]
subprocess.call(['git', 'reset', '--soft', terminal_commit])
subprocess.call(['git', 'commit', '--amend', '--no-edit'])
subprocess.call(['git', 'push', 'origin', merge_branch, '-f'])
if sys.argv[3]:
    subprocess.call(['git', 'commit', '--amend', '-m', sys.argv[3]])
