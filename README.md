# pkgsizes

> Script prints a table with ACTUAL sizes of packages in Arch Linux.  
> Описание на русском: [README.ru.md](README.ru.md).

[![ArchLinux](https://img.shields.io/badge/distribution-Arch%20Linux-blue.svg)](https://www.archlinux.org/)
[![AUR package](https://repology.org/badge/version-for-repo/aur/pkgsizes.svg)](https://repology.org/metapackage/pkgsizes)
[![made-with-python](https://img.shields.io/badge/made%20with-Python-yellow.svg)](https://www.python.org/)
[![GPL license](https://img.shields.io/badge/license-GPL-yellowgreen.svg)](https://www.gnu.org/licenses/gpl.html)

```
Name               Installed_Size  Depends_On  Full_Size  Used_By  Shared_Size  Relative_Size
libreoffice-still  416.7MiB        161         1.4GiB     0        0.0          638.0MiB
chromium           161.1MiB        214         1.1GiB     0        0.0          189.3MiB
.....
glibc              41.4MiB         4           51.1MiB    728      58.2KiB      41.4MiB
icu                35.1MiB         9           202.9MiB   155      231.9KiB     35.4MiB
.....
```
The script bypasses the dependency tree for each installed package from the local database and prints a table with fields:
* Name - package name;
* Installed_Size - own installed size;
* Depends_On - number of all dependencies;
* Full_Size - full package size with all dependencies;
* Used_By - number of packages that uses this package;
* Shared_Size - shared size that can be attributed to each package
  that uses this package (the installed size divided by the number
  of packages needing this package);
* Relative_Size - relatively ***honest size*** size which includes its own
  installed size plus the sum of shared sizes of all its dependencies.

The table is sorted by Relative_Size in descending order.

## Features
* Calculating the relative size of the package with all dependencies. It allows you to more realistically estimate the size of the package in your particular system.
* When the dependency tree is traversed then consistency checks are performed and you will be warn about possible issues. This allows you to learn more about the features of your installation.
* One Python script without third-party libraries.

### Alternative implementation
The repository contains an alternative version of this script named 'pkgsizes_pactree.py'. It achieves full correspondence of its results with the output of command 'pactree -r -u'. Although the cost of this may be a small discrepancy in the number of dependent and required packages. See ['The problem of multiple providers for the same package'](#the-problem-of-multiple-providers-for-the-same-package) in the detailed description.

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

    python3 pkgsizes.py > pkgsizes.txt

> The data table is output to standard stream. Warnings and additional information are printed to error stream.

View the whole table:  
`cat pkgsizes.txt | column -t | less`

The first 20 lines are the packages with the largest relative sizes:  
`cat pkgsizes.txt | head -20 | column -t | less`

Filter packages with Python:  
`cat pkgsizes.txt | grep python | column -t | less`

Sort by Installed_Size(2) descending:  
`cat pkgsizes.txt | sort -hrk 2 | column -t | less`

Show only columns Name(1) and Relative_Size(7):  
`cat pkgsizes.txt | awk '{print $1" "$7}' | column -t | less`

Output Name(1) and Relative_Size(7) where Used_By(5) is 0, i.e. packages are not used by other packages:  
`cat pkgsizes.txt | awk '$5 == 0 { print $1" "$7 }' | column -t | less`

---

### The problem of multiple providers for the same package
When the dependency tree is traversed the following collision may occur.
A package may have a dependency whose functionality in the system can be provided by several packages. For example, the package 'chromium' has a dependency 'ttf-font' with several providers: 'ttf-dejavu', 'ttf-droid', 'ttf-liberation', ... In this case for the dependency tree the first one will be selected - 'ttf-dejavu'. The utility 'pactree' does the same. But if you run 'pactree' with the -r option then the package 'chromium' will be specified for all font packages as Required_By. Although only one of them appeared in the tree 'chromium', as it was said.

There is a logical inconsistency. The utility 'pactree' serves for the analysis of one package, therefore such nuances are not essential there. But for the purity of the analysis and verification of results using 'pactree', an alternative version of the script was developed - 'pkgsizes_pactree.py'.

'pkgsizes_pactree.py' solves the problem as follows.  
The dependency tree for each package is built not only from the top to the bottom but also from the bottom to the top. When building tree "top-down" in case of finding several providers for one package the first one is used - both in the main version of the program and in the command `pactree <package>`. And for a tree "bottom-up" all providers are used, only in this case it is possible to take into account the full amount of Used_By. And this is the only way to ensure that the results match the `pactree -r <package>` command. As a result, the calculated fields - 'Shared_Size' and 'Relative_Size' for these two versions of the script may differ slightly.

Because of the double traversing the dependency tree, 'pkgsizes_pactree.py' runs slower than the main implementation. Therefore this version is proposed to be used to search for discrepancies with 'pactree', if this is critical. For the declared purposes of the program the basic version - 'pkgsizes.py' is fully suited.

## The idea of ​​the script

The need to sort packagers by sizes led me to the thread of forum where Allan McRae posted the 'bigpkg' script to analyze the packages by their relative sizes.  
Here is that topic:
<https://bbs.archlinux.org/viewtopic.php?id=73098>

From that script the idea of ​​a relatively honest size was taken. This script was written from scratch with a more pythonic approach. And most importantly all calculated values ​​are not hidden from the user but they are printed in the table.

## Credits

Based on the idea:  
bigpkg - find packages that require a lot of space on your system  
Copyright © 2009-2011  Allan McRae <allan@archlinux.org> 


## License

pkgsizes - print a table with ACTUAL sizes of packages in Arch Linux  
Copyright © 2018  [Andrey Balandin](https://github.com/AndreyBalandin)  
Released under the [GPL3 License](LICENSE).
