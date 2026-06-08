#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# Run tests against an installed wheel instead of the source tree.
# Proves packaging is complete: no missing __init__.py, wrong package_dir, etc.
#
# Usage:  ./scripts/test_wheel.py tests/lib/bes/common/test_algorithm.py [...]
#
# All build artifacts (source copy, wheel, venv) live under a single temp dir
# and are deleted on success.  On failure the dir is kept and its path printed.

import glob, os, os.path as path, shutil, subprocess, sys, tempfile

def _find_project_root():
  d = path.abspath(path.dirname(__file__))
  while True:
    if path.exists(path.join(d, 'pyproject.toml')):
      return d
    parent = path.dirname(d)
    if parent == d:
      sys.exit('error: cannot find pyproject.toml above ' + path.dirname(__file__))
    d = parent

def _p(msg=''):
  print(msg, flush=True)

def _run(cmd, **kwargs):
  _p('+ ' + ' '.join(str(a) for a in cmd))
  subprocess.run(cmd, check=True, **kwargs)

def main():
  if not sys.argv[1:]:
    sys.exit('usage: test_wheel.py <test_file> [...]')

  project_root = _find_project_root()

  # Resolve all test paths against caller CWD before anything changes.
  test_files = [path.abspath(f) for f in sys.argv[1:]]
  missing = [f for f in test_files if not path.exists(f)]
  if missing:
    sys.exit('error: not found:\n  ' + '\n  '.join(missing))

  tmpdir = tempfile.mkdtemp(prefix='bes_wheel_test_',
                             dir=os.environ.get('TMPDIR') or '/tmp')
  src_dir  = path.join(tmpdir, 'src')
  dist_dir = path.join(tmpdir, 'dist')
  venv_dir = path.join(tmpdir, 'venv')

  _p(f'work dir : {tmpdir}')
  _p(f'project  : {project_root}')
  _p()

  success = False
  try:
    # --- copy source so egg-info / build/ droppings never touch the repo ---
    _p('==> copying source tree')
    shutil.copytree(
      project_root, src_dir,
      ignore=shutil.ignore_patterns(
        '.git', '.venv', '__pycache__', '*.pyc', '*.pyo',
        'dist', '*.egg-info', 'build',
      ),
      ignore_dangling_symlinks=True,
    )

    # --- build wheel --------------------------------------------------------
    _p('\n==> building wheel')
    _run(['uv', 'build', '--wheel', '--out-dir', dist_dir], cwd=src_dir)

    wheels = glob.glob(path.join(dist_dir, '*.whl'))
    if len(wheels) != 1:
      sys.exit(f'error: expected 1 wheel, found {len(wheels)}: {wheels}')
    wheel = wheels[0]
    _p(f'wheel    : {path.basename(wheel)}')

    # --- isolated venv + install -------------------------------------------
    _p('\n==> creating venv')
    _run(['uv', 'venv', '--python', sys.version.split()[0], venv_dir])

    venv_python = path.join(venv_dir, 'bin', 'python')

    _p('\n==> installing wheel + pytest')
    _run(['uv', 'pip', 'install', '--python', venv_python, wheel, 'pytest'])

    # --- run tests ----------------------------------------------------------
    # Clear PYTHONPATH entirely so the source lib/ cannot shadow the wheel.
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}

    _p('\n==> running tests against wheel')
    _p('+ ' + ' '.join([venv_python, '-m', 'pytest', '-v'] + test_files))
    result = subprocess.run(
      [venv_python, '-m', 'pytest', '-v'] + test_files,
      cwd=project_root,
      env=env,
    )
    success = result.returncode == 0
    return result.returncode

  except subprocess.CalledProcessError as ex:
    _p(f'\nerror: command failed (exit {ex.returncode})')
    return ex.returncode

  finally:
    _p()
    if success:
      shutil.rmtree(tmpdir, ignore_errors=True)
    else:
      _p(f'artifacts kept for inspection: {tmpdir}')
      _p(f'  wheel  : {dist_dir}')
      _p(f'  venv   : {venv_dir}')
      _p(f'  python : {path.join(venv_dir, "bin", "python")}')

if __name__ == '__main__':
  sys.exit(main())
