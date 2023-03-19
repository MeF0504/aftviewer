import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from pyviewerlib import debug_print, cprint


def update_err(cmd):
    cprint('failed to run {}. please check {}'.format(
        ' '.join(cmd), Path(__file__).parent.parent),
        fg='r', file=sys.stderr)


def update():
    import subprocess
    os.chdir(Path(__file__).parent)
    # ~~~~~~~~~~~~~~~ fetch ~~~~~~~~~~~~~~~
    cmd = 'git fetch'.split()
    cprint('running "{}"...'.format(' '.join(cmd)), fg='y')
    stat = subprocess.run(cmd)
    if stat.returncode != 0:
        cprint(stat.stderr.decode(), fg='r')
        update_err(cmd)
        return
    # ~~~~~~~~~~~~~~~ show log ~~~~~~~~~~~~~~~
    cmd = ['git', 'log', 'HEAD..origin/main', '--pretty=format:%h (%ai); %s']
    stat = subprocess.run(cmd, capture_output=True)
    debug_print('log std out: \n{}'.format(stat.stdout.decode()))
    debug_print('log std err: \n{}'.format(stat.stderr.decode()))
    if len(stat.stderr+stat.stdout) == 0:
        # no update
        cprint('already updated.', fg='y')
        return
    else:
        cprint('update log;', fg='y')
        for out in [stat.stdout.decode(), stat.stderr.decode()]:
            if out:
                if out.endswith('\n'):
                    end = ''
                else:
                    end = '\n'
                print(out, end=end)
    # ~~~~~~~~~~~~~~~ merge ~~~~~~~~~~~~~~~
    cmd = 'git merge'.split()
    cprint('running "{}"...'.format(' '.join(cmd)), fg='y')
    stat = subprocess.run(cmd)
    if stat.returncode != 0:
        update_err(cmd)
        return
    # ~~~~~~~~~~~~~~~ submodule update ~~~~~~~~~~~~~~~
    # 開発時は↓をつけないとだけど，user的には上で十分？
    # cmd = 'git submodule update --remote --merge'.split()
    cmd = 'git submodule update'.split()
    cprint('running "{}"...'.format(' '.join(cmd)), fg='y')
    stat = subprocess.run(cmd)
    if stat.returncode != 0:
        update_err(cmd)
        return
