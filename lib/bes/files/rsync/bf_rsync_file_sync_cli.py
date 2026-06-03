#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import sys

from bes.files.bf_size import bf_size

from .bf_rsync_file_sync import bf_rsync_file_sync

class bf_rsync_file_sync_cli(object):

  @classmethod
  def run(clazz):
    parser = argparse.ArgumentParser(
      prog='bfile-sync',
      description='Sync large files to a NAS over rsync+SSH with retry and checksum verification.',
    )
    parser.add_argument('ssh_key', help='Path to SSH private key')
    parser.add_argument('destination', help='Remote destination in host:path form')
    parser.add_argument('source_dirs', nargs='+', metavar='source_dir',
                        help='One or more local directories to sync from')
    parser.add_argument('--log-file', default=None, metavar='PATH',
                        help='Write operational log to this file (default: stdout only)')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Show what would be transferred without moving any data')
    parser.add_argument('--simplify', action='store_true', default=False,
                        help='Simplify destination filenames: lowercase, strip diacritics, replace spaces/punctuation with underscores')
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--compact', action='store_true', default=False,
                            help='One line per file with in-place overwrite (default on TTY)')
    mode_group.add_argument('--verbose', action='store_true', default=False,
                            help='Two lines plus blank separator per file (default when not a TTY)')
    parser.add_argument('--min-size', default=None, metavar='SIZE',
                        help='Skip files smaller than SIZE (e.g. 100, 500k, 10M, 1G)')
    parser.add_argument('--max-size', default=None, metavar='SIZE',
                        help='Skip files larger than SIZE (e.g. 100, 500k, 10M, 1G)')
    parser.add_argument('--mime-type', default=None, metavar='MIME_TYPE',
                        help='Include only files matching this mime type (e.g. image/jpeg, video/*, audio/*)')
    args = parser.parse_args()

    if args.compact:
      compact = True
    elif args.verbose:
      compact = False
    else:
      compact = None

    try:
      min_size = bf_size.parse_size(args.min_size) if args.min_size else None
      max_size = bf_size.parse_size(args.max_size) if args.max_size else None
    except ValueError as ex:
      parser.error(str(ex))

    syncer = bf_rsync_file_sync(
      args.ssh_key,
      args.destination,
      args.source_dirs,
      log_file=args.log_file,
      dry_run=args.dry_run,
      compact=compact,
      simplify=args.simplify,
      min_size=min_size,
      max_size=max_size,
      mime_type=args.mime_type,
    )
    syncer.run()
