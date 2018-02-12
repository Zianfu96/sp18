#!/usr/bin/env python
"""Package a lecture directory for upload to website.

Using *only files that have been added to git*, it creates:

- html versions of all notebooks.
- a file named code.zip that contains python scripts, notebooks and `data/` directory.

It then prints the YAML block to paste into the lectures.yml file.  This uses the file names as default descriptions (minus extensions), so feel free to edit to taste.
"""


import sys

from pathlib import Path
from subprocess import getstatusoutput, run
from zipfile import ZipFile


def shout(cmd):
    ecode, out = getstatusoutput(cmd)
    if ecode:
        print(f"*** ERROR *** with cmd: {cmd}", file=sys.stderr)
        print("Exiting.", file=sys.stderr)
        sys.exit(ecode)

    return out.splitlines()


def init(argv=None):
    """Initialization and command-line processing."""

    # Names and default values for command-line options
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-x', '--execute', action='store_true',
                        help="Execute notebooks during HTML conversion.")
    # Process command line.
    return parser.parse_args(argv)


def main(argv=None):
    """
    Run as main script.
    """
    argv = sys.argv[1:] if argv is None else argv

    opt = init(argv)

    notebooks = shout('git ls-files *.ipynb')
    scripts = shout('git ls-files *.py')
    data = shout('git ls-files data/')
    slides = shout('git ls-files *pptx *pdf')

    code_files = notebooks + scripts + data

    # Create zip archive
    with ZipFile('code.zip', 'w') as codez:
        for f in code_files:
            codez.write(f)

    # Convert notebooks to html
    nb_html = []
    cmd = ['jupyter', 'nbconvert', '--to', 'html']
    print("*** Converting notebooks to HTML -", end='')
    if opt.execute:
        cmd.append('--execute')
        print("with execution:\n")
    else:
        print("no execution:\n")

    for nb in notebooks:
        run(cmd + [nb], check=True)
        nb_html.append(nb.replace('.ipynb', '.html'))

    # Print yaml links
    cwd = Path.cwd()
    lecname = cwd.stem

    print()
    print("*"*50)
    print("*** YAML block for lectures.yml file ***")
    print("*"*50 + "\n")
    print(f'  links:')
    for s in slides:
        s = Path(s)
        print(f"    - name: {s.stem} ({s.suffix[1:].upper()})")
        print(f'      url: assets/lectures/{lecname}/{s}')
        
    for nbh in nb_html:
        print(f"    - name: {nbh.replace('.html', '')} notebook (HTML Version)")
        print(f'      url: assets/lectures/{lecname}/{nbh}')
    print(f"    - name: code and data (includes notebooks and scripts as needed)")
    print(f'      url: assets/lectures/{lecname}/code.zip')
    # Success exit code
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
