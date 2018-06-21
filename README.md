# pkgsizes

> Script prints a table with ACTUAL sizes of packages in Arch Linux.  
> Описание на русском: [README.ru.md](README.ru.md).

[![ArchLinux](https://img.shields.io/badge/distribution-Arch%20Linux-blue.svg)](https://www.archlinux.org/)
[![made-with-python](https://img.shields.io/badge/made%20with-Python-yellow.svg)](https://www.python.org/)
[![GPL license](https://img.shields.io/badge/license-GPL-yellowgreen.svg)](https://www.gnu.org/licenses/gpl.html)

```
Name               Installed_Size  Depends_On  Full_Size  Used_By  Shared_Size  Relative_Size
libreoffice-still  416.7MiB        161         1.4GiB     0        0.0          638.0MiB
chromium           161.1MiB        214         1.1GiB     0        0.0          189.3MiB
.....
glibc               41.4MiB        4           51.1MiB    728      58.2KiB      41.4MiB
icu                 35.1MiB        9           202.9MiB   155      231.9KiB     35.4MiB
.....
```
The script bypasses the dependency tree for each installed package from the local database and prints a table with fields:
* Name - package name;
* Installed_Size - own installed size;
* Depends_On - number of all dependencies;
* Full_Size - full package size with all dependencies;
* Used_By - number of packages that uses this package;
* Shared_Size - shared size that can be attributed to each package that uses this package;
* Relative_Size - relatively ***honest size*** which includes its own installed size and the sum of shared sizes of used packages.

The table is sorted by Relative_Size in descending order.

## Features
* Calculating the relative size of the package with all dependencies. It allows you to more realistically estimate the size of the package in your particular system.
* When the dependency tree is traversed consistency checks are performed - you will be warn about possible problems. This will allow you to learn more about the features of your installation.
* One Python script without third-party libraries.

---

## Installation

> Prerequisites:  
> - common Linux utils: bash, column, sort, less, awk,..
> - Python 3.6

Copy the script to your current directory:

    curl -LO https://github.com/AndreyBalandin/archlinux-pkgsizes/raw/master/pkgsizes.py

## Usage

> The script **advisedly** does not use options and arguments to create filters, sorts (except default), formatting, etc.
> It is suggested to use the command line tools to work with the table.

Run script and save the table to a file:

    python pkgsizes.py > pkgsizes.txt

View the whole table:

    cat pkgsizes.txt | column -t | less

The first 20 lines are the packages with the largest relative sizes:

    cat pkgsizes.txt | head -20 | column -t | less

Filter packages with Python:

    cat pkgsizes.txt | grep python | column -t | less

Sort by Installed_Size(2) descending:

    cat pkgsizes.txt | sort -hrk 2 | column -t | less

Show only columns Name(1) and Relative_Size(7):

    cat pkgsizes.txt | awk '{print $1"\t"$7}' | less

Output Name(1) and Relative_Size(7) for those rows for which the Used_By (5) field is 0, i.e. packages not used by other packages:

    cat pkgsizes.txt | awk '$5 == 0 { print $1"\t"$7 }' | column -t | less

---

## The idea of ​​the script

The need to sort packagers by size led me to the thread of forum where Allan McRae posted the 'bigpkg' script to analyze the packages by their relative sizes.  
Here is that topic:
<https://bbs.archlinux.org/viewtopic.php?id=73098>

From that script the idea of ​​a relatively honest size was taken. This script was written from scratch with a more pythonic approach. And most importantly all calculated values ​​are not hidden from the user but they are printed in the table.

## Credits

Based on the idea:  
bigpkg - find packages that require a lot of space on your system  
Copyright © 2009-2011 by Allan McRae <allan@archlinux.org> 


## License

pkgsizes - print a table with ACTUAL sizes of packages in Arch Linux  
Copyright © 2018  [Andrey Balandin](https://github.com/AndreyBalandin)  
Released under the [GPL3 License](LICENSE).
