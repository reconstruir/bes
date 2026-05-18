#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import time
from datetime import datetime

from bes.system.check import check
from bes.system.log import logger
from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
from bes.files.bf_filename import bf_filename
from bes.ssh.bssh_command import bssh_command

from .bf_rsync_command import bf_rsync_command
from .bf_rsync_error import bf_rsync_error

class bf_rsync_file_sync(object):
  'Sync files from local dirs to a remote NAS over rsync+SSH with retry and checksum verification.'

  _log = logger('bf_rsync_file_sync')

  RETRY_WAIT_SECONDS = 30

  def __init__(self, ssh_key, destination, source_dirs,
               log_file=None, known_hosts_file=None, strict_host_checking=True,
               retry_wait_seconds=None, ssh_port=None):
    check.check_string(ssh_key)
    check.check_string(destination)
    check.check_string_seq(source_dirs)
    check.check_string(log_file, allow_none=True)
    check.check_string(known_hosts_file, allow_none=True)
    check.check_bool(strict_host_checking)
    check.check_int(retry_wait_seconds, allow_none=True)
    check.check_int(ssh_port, allow_none=True)

    if not path.exists(ssh_key):
      raise bf_rsync_error(f'ssh key not found: {ssh_key}')
    if ':' not in destination:
      raise bf_rsync_error(f'destination must be host:path, got: {destination}')

    self._ssh_key = path.abspath(ssh_key)
    self._host, _, self._dest_root = destination.partition(':')
    self._source_dirs = [path.abspath(d) for d in source_dirs]
    self._log_file = log_file
    self._known_hosts_file = known_hosts_file
    self._strict_host_checking = strict_host_checking
    self._retry_wait_seconds = retry_wait_seconds if retry_wait_seconds is not None else self.RETRY_WAIT_SECONDS
    self._ssh_port = ssh_port
    self._log_fh = None

  def run(self):
    'Run the sync loop until all files are transferred. Never returns on permanent failure.'
    if self._log_file:
      self._log_fh = open(self._log_file, 'a', encoding='utf-8')
    try:
      self._run_loop()
    finally:
      if self._log_fh:
        self._log_fh.close()
        self._log_fh = None

  def _run_loop(self):
    pending = self._collect_files()
    while pending:
      failed = False
      completed = []
      for src in pending:
        try:
          self._sync_one(src)
          completed.append(src)
        except Exception as ex:
          self._emit('RETRY', f'error on {path.basename(src)}: {ex}, waiting {self._retry_wait_seconds}s...')
          self._log.log_e(f'sync error: {ex}')
          failed = True
          break
      pending = [f for f in pending if f not in completed]
      if failed:
        time.sleep(self._retry_wait_seconds)
    self._cleanup_partial()

  def _collect_files(self):
    files = []
    for src_dir in self._source_dirs:
      if not path.isdir(src_dir):
        self._emit('ERROR', f'source dir not found: {src_dir}')
        continue
      for entry in sorted(os.listdir(src_dir)):
        if entry == '.DS_Store':
          continue
        full = path.join(src_dir, entry)
        if path.isfile(full):
          files.append(full)
    return files

  def _sync_one(self, src):
    basename = path.basename(src)
    local_hash = bf_checksum_cache.get_checksum(src, 'sha256')
    remote_hash = self._ssh_sha256(f'{self._dest_root}/{basename}')

    if remote_hash is None:
      dest_path = f'{self._dest_root}/{basename}'
    elif remote_hash == local_hash:
      self._emit('SKIP', f'{basename} — destination exists, same checksum')
      os.remove(src)
      self._emit('DELETED', f'{basename} — source removed')
      return
    else:
      unique_name = self._make_unique_name(basename, local_hash)
      dest_path = f'{self._dest_root}/{unique_name}'
      self._emit('RENAME', f'{basename} → {unique_name} — destination exists, different content')

    self._emit('TRANSFER', f'{basename} → {self._host}:{dest_path}')
    self._rsync(src, dest_path)

    verified_hash = self._ssh_sha256(dest_path)
    if verified_hash != local_hash:
      raise bf_rsync_error(f'checksum mismatch after transfer: {basename}')
    self._emit('VERIFIED', f'{basename} — checksum confirmed on NAS')

    os.remove(src)
    self._emit('DELETED', f'{basename} — source removed')

  def _rsync(self, src, dest_path):
    ssh_cmd = f'ssh -i {self._ssh_key}'
    if self._ssh_port is not None:
      ssh_cmd += f' -p {self._ssh_port}'
    if not self._strict_host_checking:
      ssh_cmd += ' -o StrictHostKeyChecking=no'
    if self._known_hosts_file:
      ssh_cmd += f' -o UserKnownHostsFile={self._known_hosts_file}'
    cmd = [
      '--partial', '--partial-dir=.rsync-partial',
      '--exclude=**/.DS_Store',
      '--human-readable', '--stats',
      '-va',
      '-e', ssh_cmd,
      src,
      f'{self._host}:{dest_path}',
    ]
    bf_rsync_command.call_command(cmd, quote=False)

  def _ssh_sha256(self, remote_path):
    'Return sha256 of remote_path, or None if the file is missing.'
    ssh_args = ['-i', self._ssh_key, '-o', 'BatchMode=yes']
    if self._ssh_port is not None:
      ssh_args += ['-p', str(self._ssh_port)]
    if not self._strict_host_checking:
      ssh_args += ['-o', 'StrictHostKeyChecking=no']
    if self._known_hosts_file:
      ssh_args += ['-o', f'UserKnownHostsFile={self._known_hosts_file}']
    remote_cmd = f'sha256sum "{remote_path}" 2>/dev/null || echo MISSING'
    ssh_args += [self._host, remote_cmd]
    rv = bssh_command.call_command(ssh_args, quote=False)
    output = rv.stdout.strip()
    if output == 'MISSING' or not output:
      return None
    return output.split()[0].lower()

  def _cleanup_partial(self):
    'Best-effort removal of .rsync-partial dir on the NAS after a clean run.'
    try:
      ssh_args = ['-i', self._ssh_key, '-o', 'BatchMode=yes']
      if self._ssh_port is not None:
        ssh_args += ['-p', str(self._ssh_port)]
      if not self._strict_host_checking:
        ssh_args += ['-o', 'StrictHostKeyChecking=no']
      if self._known_hosts_file:
        ssh_args += ['-o', f'UserKnownHostsFile={self._known_hosts_file}']
      ssh_args += [self._host, f'rm -rf "{self._dest_root}/.rsync-partial"']
      bssh_command.call_command(ssh_args, quote=False)
      self._emit('CLEANUP', f'{self._host}:{self._dest_root}/.rsync-partial removed')
    except Exception as ex:
      self._log.log_w(f'cleanup of .rsync-partial failed (non-fatal): {ex}')

  @staticmethod
  def _make_unique_name(basename, source_hash):
    stem = bf_filename.without_extension(basename)
    ext = bf_filename.extension(basename)
    new_stem = f'{stem}-{source_hash[:8]}'
    return bf_filename.add_extension(new_stem, ext) if ext else new_stem

  def _emit(self, tag, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'{ts} [{tag:<8}] {message}'
    print(line, flush=True)
    if self._log_fh:
      self._log_fh.write(line + '\n')
      self._log_fh.flush()
