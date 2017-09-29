.. _publish-package.rst:

Publishing the Package to a Package Repository
==============================================

As you make changes to this library, you'll probably want to publish them so that consuming applications can benefit.
*(That's the point, right?)*  This article discusses that process.

Modifying Your ``.pypirc`` File
-------------------------------

To keep life a little simpler, you probably want to modify your ``.pypirc`` file to include information about your new
repository server.  You can do this by adding an alias for the server in your list of *index-servers*. When you're
finished, your ``.pypirc`` file might look something like the one below assuming your give your new repository
**geocomm** as an alias.

On Windows, you'll find this file at ``C:\Users\%USERNAME%\.pypirc``.

.. note::
    If you currently do not have this file, you will need to create one in the location mentioned above.

.. code-block:: ini

    [distutils]
    index-servers =
      pypi
      pypitest
      geocomm

    [pypi]
    username=<pypi_user>
    password=<pypi_password>

    [pypitest]
    username=<pypitest_user>
    password=<pypitest_password>

    [geocomm]
    repository: http://192.168.11.115:8080
    username: geocomm
    password: 7h5k3w-gcc

    [fury]
    repository: https://pypi.fury.io/geocomm/
    username: YOURSPECIALSTRING
    password:

.. note::
    There are refinements to this process and we'll update this document as we go along.