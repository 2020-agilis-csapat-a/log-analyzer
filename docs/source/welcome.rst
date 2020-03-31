.. _welcome:

=========================
Hello world / DUMMY!!!!!!
=========================

.. Important::

    Please read instal guide to make sure you installed Python and Docker correctly.

    * Docker needs to be version 1.9 or higher
    * Python 3.4 or higher including pip is required
    * Make sure your console environment is UTF-8 (``export LC_ALL=en_US.utf-8; export LANG=en_US.utf-8``)


This guide should show all steps for one sample application from birth to death.
Please see the other sections in the information about specific topics.

Install STUPS command line tools and configure them.

.. code-block:: bash

    $ sudo pip3 install --upgrade stups
    $ stups configure

First of all clone this example project:

.. code-block:: bash

    $ git clone https://github.com/zalando-stups/zalando-cheat-sheet-generator.git
    $ cd zalando-cheat-sheet-generator
