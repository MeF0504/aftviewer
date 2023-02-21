import os
import sys
from pathlib import Path
import subprocess

if len(sys.argv) > 1:
    install_path = Path(sys.argv[1])
else:
    install_path = Path('~/.pyviewer').expanduser()
if install_path.exists():
    print('{} already exists.'.format(install_path))
    exit()

subprocess.run(['git', 'clone', 'https://github.com/MeF0504/pyviewer.git', install_path])
os.chdir(install_path)
subprocess.run(['git', 'submodule', 'update', '--init'])

if 'PATH' in os.environ \
   and str(install_path/'bin') not in os.environ['PATH'].split(os.pathsep):
    print('\nplease add {} to your PATH.'.format(install_path/'bin'))
if 'SHELL' in os.environ and 'zsh' in os.environ['SHELL']:
    zsh_cmp = install_path/'shell/completion.zsh'
    print('\nplease add \'[ -f "{}" ] && source "{}"\' in your .zshrc.'.format(
        zsh_cmp, zsh_cmp))
