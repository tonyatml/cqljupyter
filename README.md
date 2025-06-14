[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Downloads](https://pepy.tech/badge/cqljupyter)](https://pepy.tech/project/cqljupyter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cqljupyter)
[![PyPI version](https://badge.fury.io/py/cqljupyter.svg)](https://badge.fury.io/py/cqljupyter)

A Jupyter kernel for Apache Cassandra

To install:

    pip install cqljupyter

To configure the Cassandra host or IP address:

    python -m cqljupyter.install  [<hostname> <port>] [--ssl] [-u user] [-p password]

You can always rerun the above command to change the connection. It's best to restart Jupyter after running it. 
You can often get away with closing your notebook, and then refreshing the main Jupyter page too, but that's
error-prone.

then start the notebook:

    jupyter notebook

In the notebook interface, select **CQL** from the **New** menu

To run the sample CQL:

    jupyter notebook Sample.ipynb

Dev mode
========

- Clone this repo _and check out to this branch_
- Go to a new, clean directory
- Create a new virtualenv (I did 3.12)
- `pip install -e <dir_of_cloned_repo>`
- `python -m cqljupyter.install  [<hostname> <port>] [--ssl] [-u user] [-p password]`

_Note: I ended up with `cqlsh==6.2.0`. Presumably the cqlsh version is the reason why I needed to tweak the code._

Start with `jupyter notebook`, open in browser, try a CQL kernel.

Syntax
======

All standard CQL syntax is supported since this package reuses the CQLSH python module.

Auto-complete
-------------

Use the **TAB** key to invoke auto-complete

HTML
----

If you start a cell with **%%html**, the html will be returned and rendered

Build
=====
Build using:

    python -m build

Implementation Notes
====================

For details of how Jupyter kernels work, see these references:
* [Making simple Python wrapper kernels](http://jupyter-client.readthedocs.org/en/latest/wrapperkernels.html)
* [Making kernels for Jupyter](https://jupyter-client.readthedocs.io/en/stable/kernels.html)

Author
======

This package was developed by Brad Schoening for Python 3. It is based upon earlier work 
by Steve Lowenthal and uses the open source Apache Cassandra CQLSH library.

License
=======

This project is licensed under the terms of the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).
