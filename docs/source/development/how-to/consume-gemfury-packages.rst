.. _consume-gemfury-packages.rst:

Consuming GemFury Packages
===========================

In order for us to easily add and ultimately consume PyPI, NuGet, and other packages from our private GemFury repository.

After signing up with GemFury, you will want to grab your special string from GeoComm's implementations.


|  **Example** https://YOURSPECIALSTRING@repo.fury.io/geocomm/

The addition to our pip configuration file will allow us to add packages into our requirements.txt file without having to write the URL in the file itself.

Windows
-------
On Windows, you will find this file at: ``C:\Users\%USERNAME%\AppData\Roaming\pip\pip.ini``


.. note::
    If you currently do not have this file, you will need to create one at the location mentioned above.

.. code-block:: ini

    [global]
    extra-index-url = --extra-index-url https://pypi.fury.io/YOURSPECIALSTRING/geocomm/

Linux
-----
On Linux, you will want to find this file ``/etc/pip.conf``

.. note::
    If you currently do not have this file, you will need to create one at the location mentioned above.

.. code-block:: ini

    [content]
    extra-index-url = --extra-index-url https://pypi.fury.io/YOURSPECIALSTRING/geocomm/

.. note::
    There are refinements to this process and we'll update this document as we go along.