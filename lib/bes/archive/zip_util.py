"""This module containse logic related to archive_zip.

Examples:

  Create zip archive without size report:

    zp = zip_utils("test.zip", size_report=False)
    zp.create_all(["root_dir"])

  Create zip archive with size report (print first 100 lines):

    zp = zip_utils("test.zip")
    zp.create_all(["root_dir"])

  Create zip archive with size report (save report to file with 100 lines):

    zp = zip_utils("test.zip", size_report_output="size_report.txt")
    zp.create_all(["root_dir"])

  Create zip archive with size report (print 450 lines):

    zp = zip_utils("test.zip", size_report_limit=450)
    zp.create_all(["root_dir"])

"""

import os
import sys
import zipfile

from bes.fs.file_util import file_util

from .archive_zip import archive_zip


class zip_util(object):
  """Utils class for archive_zip.

  Attributes:
    filename: The name of zip file.
    size_report: If True, then it will enable size report. Otherwise, disable it.
                 Default value is True.
    size_report_limit: Amount of files to show inside size report. Default value is 100.
    size_report_output: The output filename. Default value is None. If None, then just print it,
                        otherwise, save to the output file.
  """

  def __init__(self, filename, size_report=True, size_report_limit=100, size_report_output=None):
    self._filename = filename
    self._size_report = size_report
    self._size_report_limit = size_report_limit
    self._size_report_output = size_report_output
    self._archive = archive_zip(filename)

  def create_all(self, entry_points, base_dir=None, extra_items=None, include=None, exclude=None, extension=None):
    """Create a zip archive for all entry points (each entry point can be a folder, like root dir, or a specific file).
    It will combine all folders and files into one zip archive.

    Args:
      entry_points: List of entry points.
      base_dir: Base directory name that will be used to create an acrname. Default value is None.
      extra_items: List of items-objects (each item is namedtuple('item', [ 'filename', 'arcname' ]))
                   that will be added to the final zip. Default value is None.
      include: String patterns that will be used to include files to final zip. Default value is None.
      exclude: String patterns that will be used to exclude files from final zip. Default value is None.
      extension: Extension of acrchive. Default value is None
    """
    self._archive._pre_create()
    items = self._collect_items(entry_points, base_dir, extra_items, include, exclude)

    if self._size_report:
      self._create_size_report(items)

    self._create_zipfile(items)

  def _collect_items(self, entry_points, base_dir, extra_items, include, exclude):
    items = []

    for entry_point in entry_points:
      if os.path.isdir(entry_point):
        # TODO: the correct method call should look like self._archive.find() but not self._archive._find()
        # because we are accessing private method outside of specific object (archive_zip object)
        entry_point_items = self._archive._find(entry_point, base_dir, extra_items, include, exclude)
        items.extend(entry_point_items)
      else:
        arcname = os.path.join(base_dir, entry_point) if base_dir else entry_point
        items.append(self._archive.item(entry_point, arcname))

    return items

  def _create_size_report(self, items):
    size_report = []

    for item in items:
      size = os.stat(item.filename).st_size
      size_report.append((item.filename, size))

    size_report.sort(key=lambda e: e[1], reverse=True)

    if self._size_report_output:
      with open(self._size_report_output, "w") as file:
        self._save_size_report_items(size_report, file)
    else:
      self._save_size_report_items(size_report)

  def _save_size_report_items(self, size_report, file=sys.stdout):
    limit = len(size_report) if len(size_report) < self._size_report_limit else self._size_report_limit

    for index in range(limit):
      item = size_report[index]
      print("{:<20}{}".format(file_util.sizeof_fmt(item[1]), item[0]), file=file)

  def _create_zipfile(self, items):
    with zipfile.ZipFile(file=self._filename, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
      for item in items:
        archive.write(item.filename, arcname=item.arcname)
