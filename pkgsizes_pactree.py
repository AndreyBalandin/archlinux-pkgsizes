#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pkgsizes_pactree.py v0.1.0

Script prints a table with ACTUAL sizes of packages in Arch Linux.

> This is an alternative implementation of the script - 'pkgsizes.py'.
> You can read about differences from the main script and about the purpose
> of developing this version in README.md, section 'The problem of
> several providers of the same package':
> https://github.com/AndreyBalandin/archlinux-pkgsizes

The script bypasses the dependency tree for each installed package
from the local database and prints a table with fields:
  (1) Name - package name;
  (2) Installed_Size - own installed size;
  (3) Depends_On - number of all dependencies;
  (4) Full_Size - full package size with all dependencies;
  (5) Used_By - number of packages that uses this package;
  (6) Shared_Size - shared size that can be attributed to each package
      that uses this package (the installed size divided by the number
      of packages needing this package);
  (7) Relative_Size - relatively HONEST size which includes its own
      installed size plus the sum of shared sizes of all its dependencies.
The table is sorted by Relative_Size in descending order.

Usage:
  Run script and save the table to a file:
    python3 pkgsizes_pactree.py > pkgsizes.txt

Options:
  no options

Examples:
  View the whole table:
    cat pkgsizes.txt | column -t | less
  The first 20 lines are the packages with the largest relative sizes:
    cat pkgsizes.txt | head -20 | column -t | less
  Filter packages with Python:
    cat pkgsizes.txt | grep python | column -t | less
  Sort by Installed_Size(2) descending:
    cat pkgsizes.txt | sort -hrk 2 | column -t | less
  Show only columns Name(1) and Relative_Size(7):
    cat pkgsizes.txt | awk '{print $1" "$7}' | column -t | less

Based on the idea:
  bigpkg - find packages that require a lot of space on your system
  Copyright © 2009-2011  Allan McRae <allan@archlinux.org>

License:
  pkgsizes_pactree.py  Copyright © 2018  Andrey Balandin
  Repository: https://github.com/AndreyBalandin/archlinux-pkgsizes
  Released under the GPL3 License: https://www.gnu.org/licenses/gpl

"""

# ---------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------

import re
import sys

from glob import glob
from operator import attrgetter


LOCAL_DB_PATH = '/var/lib/pacman/local'


# ---------- class Package ----------


class Package:
    __slots__ = ['name', 'size', 'depends', 'provides', 'full_depends',
                 'required_by', 'full_required_by', 'full_size',
                 'shared_size', 'relative_size']

    def __init__(self, name, size, depends, provides):
        self.name = name
        self.size = size
        self.depends = depends
        self.provides = provides
        self.full_depends = []
        self.required_by = set()
        self.full_required_by = []
        self.full_size = 0
        self.shared_size = 0
        self.relative_size = 0

    def __repr__(self):
        return self.name


# ---------- Helpers Functions ----------


def warn(*args, **kwargs):
    """Print to stderr instead of stdout."""
    print(*args, file=sys.stderr, **kwargs)


def humanize(size, decimal=1, sep=''):
    """Return human readable size."""
    for unit in ['', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024:
            return f"{size:.{decimal}f}{sep}{unit}"
        size /= 1024


def strip_version(name):
    """Return name without versioning."""
    return re.split(r'[=<>]', name)[0]


# --------- Reading Local Database -------------


def parse_desc_file(filename):
    """Return the package name, size, lists of dependents and provides."""
    name = ''
    size = 0
    depends = []
    provides = []
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if line == '%NAME%':
                    name = next(file).strip()
                elif line == "%SIZE%":
                    size = int(next(file))
                elif line == "%DEPENDS%":
                    line = next(file).strip()
                    while line:
                        depends.append(line)
                        line = next(file).strip()
                elif line == "%PROVIDES%":
                    line = next(file).strip()
                    while line:
                        provides.append(line)
                        line = next(file).strip()
        if not name or name not in filename:
            name = ''
            raise UserWarning("Parse Error: package's name not found or inconsistent")
    except Exception as e:
        warn(e)
        warn('File could not be parsed:', filename)
    return name, size, depends, provides


def read_local_database():
    "Retrieve stored information about packages."
    warn('Reading local database...')
    packages = {}  # name -> Package
    providers = {}  # customer -> Package-provider
    desc_files = sorted(glob(LOCAL_DB_PATH + '/*/desc'))
    for filename in desc_files:
        name, size, depends, provides = parse_desc_file(filename)
        if not name:
            continue
        packages[name] = Package(name, size, depends, provides)
        for customer in provides:
            if customer in providers:
                # make list for multiple providers
                if isinstance(providers[customer], Package):
                    providers[customer] = [providers[customer], packages[name]]
                else:
                    providers[customer].append(packages[name])
            else:
                providers[customer] = packages[name]
            providers[strip_version(customer)] = providers[customer]
    # replace string values in 'depends' with object references
    for pkg in packages.values():
        new_depends = set()
        for dep in pkg.depends:
            repl = (packages.get(strip_version(dep)) or providers.get(dep)
                    or providers.get(strip_version(dep)))
            if repl:
                if isinstance(repl, Package):
                    new_depends.add(repl)
                    repl.required_by.add(pkg)
                else:
                    warn(f'Warning: dependence "{dep}" in package "{pkg}" '
                         f'has several providers: {repl} (script will use '
                         f'the first one for dependency tree).')
                    new_depends.add(repl[0])  # use first for dependency tree
                    for provider in repl:
                        provider.required_by.add(pkg)
            else:
                warn(f'Database Error: package "{pkg}" depends on '
                     f'"{dep}" but the local database does not contain '
                     f'information about package "{dep}".')
        pkg.depends = new_depends
    return list(packages.values())


# ---------- Processing Packages ----------


def process_packages(packages):
    """Calculate additional values for packages."""
    warn('Processing dependency trees for packages...')
    for pkg in packages:
        pkg.full_size = pkg.size
        pkg.full_depends = list(pkg.depends)
        for dep in pkg.full_depends:
            for ddep in dep.depends:
                if ddep == pkg:
                    warn(f'Warning: cyclic dependencies found "{pkg}" - "{dep}"')
                elif ddep not in pkg.full_depends:
                    pkg.full_depends.append(ddep)
            pkg.full_size += dep.size
        # build the dependency tree from bottom to top to get 'full_required_by'
        pkg.full_required_by = list(pkg.required_by)
        for dep in pkg.full_required_by:
            for ddep in dep.required_by:
                if ddep != pkg and ddep not in pkg.full_required_by:
                    pkg.full_required_by.append(ddep)
    for pkg in packages:
        if len(pkg.full_required_by) > 0:
            pkg.shared_size = pkg.size / len(pkg.full_required_by)
    for pkg in packages:
        pkg.relative_size = pkg.size + sum(dep.shared_size
                                           for dep in pkg.full_depends)

# ---------- Output Results ----------


def output(packages):
    """Output and summarize."""
    total_size = 0
    try:
        print('Name', 'Installed_Size', 'Depends_On', 'Full_Size', 'Used_By',
              'Shared_Size', 'Relative_Size', sep='\t')
        for pkg in sorted(packages, key=attrgetter('relative_size'), reverse=True):
            print(pkg.name, humanize(pkg.size), len(pkg.full_depends),
                  humanize(pkg.full_size), len(pkg.full_required_by),
                  humanize(pkg.shared_size), humanize(pkg.relative_size),
                  sep='\t')
            total_size += pkg.size
    except BrokenPipeError:
        warn('BrokenPipeError was caught. Nothing wrong. Please, save '
             'standard output to a file then analyze it with pipes.')
    warn('Processed packages:', len(packages))
    warn('Total Installed Size:', humanize(total_size, sep=' '))


# ---------- Main section ----------

if __name__ == '__main__':
    if len(sys.argv) > 1:
        warn(__doc__)
    else:
        packages = read_local_database()
        process_packages(packages)
        output(packages)
