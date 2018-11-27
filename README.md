# rebuild

**rebuild** is a set of Python (2 and 3) modules and tools to manage
the process of building, packaging, testing and publishing binary
artifacts for free software projects.

**rebuild** was inspired by existing tools: rpm, virtualenv, pip, macports

**rebuild** is a work in progress.

## Features

* Manage dependencies between projects.
* Create binary packages for projects.
* Test those artifacts in an isolated environment.
* Write simple recipes for a variety of software build systems (make, cmake, python and perl)
* Extensive API for adding support for new build tools.
* Create virtual envs for projects to use in isolated shell environments.
* Install and remove binary packages from these environments (like a personal rpm)

**rebuild** also contains python libraries for:
* Very fast detection of elf and mach-o binary formats.
* Dealing with fat binaries on macos.
* Interfacing with native package managers (rpm, deb, pkg) from python.
* Using compilation toolchains from python.
