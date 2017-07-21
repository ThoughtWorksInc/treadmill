import sys
import subprocess

uncommit_changes = subprocess.check_output(
    ['git', 'status', '--porcelain', '--untracked-files=no']
)

if uncommit_changes:
    print(
        'Please commit changes of the current branch, and then try again.'
    )
else:
    print('Preparing...')
    branch = sys.argv[1]
    merge_branch = branch.strip() + '-merge'
    subprocess.call(['git', 'checkout', branch])
    print('Deleting old branch ' + merge_branch + ' locally...')
    subprocess.call(['git', 'branch', '-D', merge_branch])
    print('Pulling latest changes...')
    subprocess.call(['git', 'pull', '--rebase'])
    subprocess.call(['git', 'checkout', '-b', merge_branch])
    terminal_commit = sys.argv[2]
    print('Rebasing and squashing...')
    subprocess.call(['git', 'reset', '--soft', terminal_commit])
    subprocess.call(['git', 'commit', '--amend', '--no-edit'])
    if (len(sys.argv) > 3) and sys.argv[3]:
        subprocess.call(['git', 'commit', '--amend', '-m', sys.argv[3]])
    print('Promoting to remote...')
    subprocess.call(['git', 'push', 'origin', merge_branch, '-f'])
    print('Synced!')
