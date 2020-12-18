# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_exe import git_exe
from .git_lfs import git_lfs
from .git_repo import git_repo
from .git_clone_options import git_clone_options

from bes.fs.temp_file import temp_file

class git_lfs_util(object):
  'Misc git lfs util.'

  @classmethod
  def lfs_invalid_files(clazz, address, branch):
    '''
    Return a list of files that are GIT LFS invalid.  That means:
    - They match the .gitattributes
    - They are not GIT LFS pointers but plain git files
    '''
    check.check_string(address)
    check.check_string(branch)

    '''\
Cloning into 'lfs-test'...
remote: Counting objects: 96, done.
remote: Compressing objects: 100% (89/89), done.
remote: Total 96 (delta 18), reused 0 (delta 0)
Receiving objects: 100% (96/96), 76.11 KiB | 1.14 MiB/s, done.
Resolving deltas: 100% (18/18), done.
Filtering content: 100% (2/2), 20.00 KiB | 7.00 KiB/s, done.
Encountered 3 file(s) that should have been pointers, but weren't:
	honeydew melon.bytes
	lemon.bytes
	subdir/organic banana.bytes
'''    
    tmp_dir = temp_file.make_temp_dir()
    repo = git_repo(tmp_dir, address = address)
    options = git_clone_options()
    options.branch = branch
    clone_rv, sub_rv = repo.clone(options = options)
    print('clone_rv: {}'.format(clone_rv))
    print('  sub_rv: {}'.format(sub_rv))
    return []
