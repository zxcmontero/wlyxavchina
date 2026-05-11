import subprocess
import os
import sys

repo_dir = r"c:\Users\Nikita\Desktop\kadr agents"
if not os.path.isdir(repo_dir):
    print('Repo dir not found:', repo_dir)
    sys.exit(2)

os.chdir(repo_dir)

def run(cmd):
    print('> ' + ' '.join(cmd))
    cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if cp.stdout:
        print(cp.stdout.strip())
    if cp.stderr:
        print(cp.stderr.strip())
    return cp

print('--- GIT PUSH SCRIPT START ---')
run(['git', 'status', '--porcelain'])
branch_cp = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
branch = branch_cp.stdout.strip() if branch_cp.stdout else ''
print('BRANCH:', branch)

add_cp = run(['git', 'add', '-A'])
commit_cp = run(['git', 'commit', '-m', 'chore: UI/content polish — sticky footer; neutral product copy'])
commit_out = (commit_cp.stdout or '') + (commit_cp.stderr or '')
if 'nothing to commit' in commit_out.lower():
    print('No changes to commit')
else:
    print('Commit result code:', commit_cp.returncode)

push_cp = run(['git', 'push', 'origin', 'HEAD:main'])
print('Push exit code:', push_cp.returncode)
print('--- GIT PUSH SCRIPT END ---')

sys.exit(push_cp.returncode)
