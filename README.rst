Introduction
============

..     :target: https://circuitpython.readthedocs.io/projects/tlc5957/en/latest/

.. image:: https://readthedocs.org/projects/slight-circuitpython-tlc5957/badge/?version=latest
    :target: https://slight-circuitpython-tlc5957.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://travis-ci.org/s-light/slight_CircuitPython_TLC5957.svg?branch=master
    :target: https://travis-ci.org/s-light/slight_CircuitPython_TLC5957
    :alt: Build Status

CircuitPython library for `TI TLC5957 48-channel 16bit LED-Driver <http://www.ti.com/product/TLC5957/>`_

Setting of LED-Values / API is similar to NeoPixel and Dotstar APIs and
compatible with `fancyled <https://circuitpython.readthedocs.io/projects/fancyled/en/latest/>`_.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

.. * `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

have a look at the `examples <examples.html>`_ subfolder

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/s-light/slight_CircuitPython_TLC5957/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Building locally
================

Zip release files
-----------------

To build this library locally you'll need to install the
`circuitpython-build-tools <https://github.com/adafruit/circuitpython-build-tools>`_ package.

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install circuitpython-build-tools

Once installed, make sure you are in the virtual environment:

.. code-block:: shell

    source .env/bin/activate

Then run the build:

.. code-block:: shell

    circuitpython-build-bundles --filename_prefix slight-circuitpython-tlc5957 --library_location .

Sphinx documentation
-----------------------

Sphinx is used to build the documentation based on rST files and comments in the code. First,
install dependencies (feel free to reuse the virtual environment from above):

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install Sphinx sphinx-rtd-theme

Now, once you have the virtual environment activated:

.. code-block:: shell

    cd docs
    sphinx-build -E -W -b html . _build/html

This will output the documentation to ``docs/_build/html``. Open the index.html in your browser to
view them. It will also (due to -W) error out on any warning like Travis will. This is a good way to
locally verify it will pass.
