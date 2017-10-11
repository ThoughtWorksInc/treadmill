import sys
import subprocess
from datetime import date


if sys.argv[1] == 'help':
    print("Usage:\npython sync.py <branch-to-be-squashed> <commit-sha-till-you-want-to-sqaus> '<commit-message>'")
else:
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
        merge_branch = branch.strip() + date.today().strftime('-%d-%m-%Y') + '-merge'
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
        current_author_name = subprocess.check_output(['git', 'config', 'user.name']).strip()
        current_author_email = subprocess.check_output(['git', 'config', 'user.email']).strip()
        author_string = current_author_name + '<' + current_author_email + '>'
        subprocess.call(['git', 'commit', '--amend', '--author=' + author_string])

        if (len(sys.argv) > 3) and sys.argv[3]:
            subprocess.call(['git', 'commit', '--amend', '-m', sys.argv[3]])

        yes = set(['yes','y', 'Y'])
        choice = raw_input('Push this [Y/n]? ').lower()
        if choice in yes:
            print('Promoting to remote...')
            subprocess.call(['git', 'push', 'origin', merge_branch, '-f'])
            print('Synced!')
        else:
            print('Branch is rebased/squashed and ready to be pushed.')

        print('\x1b[6;30;42m' + 'Good Job!!!' + '\x1b[0m')
