#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_docker_cli_args(object):

  def __init__(self):
    pass
  
  def docker_add_args(self, subparser):

    # docker:images
    p = subparser.add_parser('images', help = 'List images')
    p.add_argument('-u', '--untagged', action = 'store_true', default = False,
                   help = 'Show only untagged images. [ False ]')
    p.add_argument('--repo', action = 'store', default = None,
                   help = 'Print only the that match the given repo wildcard. [ None ]')
    p.add_argument('-s', '--style', action = 'store', default = 'table',
                   choices = ( 'brief', 'repo', 'table' ),
                   help = 'Style for output. [ table ]')

    # docker:stash_save
    p = subparser.add_parser('stash_save', help = 'Stash a bunch of images in a directory as tarballs')
    p.add_argument('repo', action = 'store', default = None,
                   help = 'Stash a bunch of images in a directory as tarballs. [ None ]')
    p.add_argument('where', action = 'store', default = None,
                   help = 'Where to stash the images.  Needs to be an empty dir. [ None ]')
    p.add_argument('-d', '--force', action = 'store_true', default = False,
                   help = 'Force removal of images even if used by containers. [ False ]')

    # docker:stash_restore
    p = subparser.add_parser('stash_restore', help = 'Restore a bunch of stashed images')
    p.add_argument('where', action = 'store', default = None,
                   help = 'Where the images got stashed.. [ None ]')
    
    # docker:backup
    p = subparser.add_parser('backup', help = 'Backup an image')
    p.add_argument('tagged_repository', action = 'store', default = None,
                   help = 'The image in repo:tag format. [ None ]')
    p.add_argument('output_archive', action = 'store', default = None,
                   help = 'The output tar.gz tarball. [ None ]')
    
    # docker:ps
    p = subparser.add_parser('ps', help = 'List containers')
    p.add_argument('-b', '--brief', action = 'store_true', default = False,
                   help = 'Print only the container id. [ False ]')
    p.add_argument('-s', '--status', action = 'store', default = None,
                   choices = ( 'running', 'exited', 'created' ),
                   help = 'Only show containers with the given status. [ None ]')

    # docker:image_inspect
    p = subparser.add_parser('image_inspect', help = 'inspect an image')
    p.add_argument('image', action = 'store', default = None,
                   help = 'The image to inspect.')
    p.add_argument('-c', '--checksum', action = 'store_true', default = False,
                   help = 'Print the checksum of the inspect data. [ False ]')

    # docker:cleanup
    p = subparser.add_parser('cleanup', help = 'Cleanup images and processes')
    p.add_argument('-i', '--untagged-images', action = 'store_true', default = False,
                   help = 'Cleanup untagged images. [ False ]')
    p.add_argument('-e', '--exited-containers', action = 'store_true', default = False,
                   help = 'Cleanup exited containers. [ False ]')
    p.add_argument('-r', '--running-containers', action = 'store_true', default = False,
                   help = 'Cleanup running containers. [ False ]')

  def _command_docker(self, command, *args, **kargs):
    from .bat_docker_cli_handler import bat_docker_cli_handler
    return bat_docker_cli_handler(kargs).handle_command(command)
