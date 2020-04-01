.. _concepts:

========
Concepts
========

.. _records:

Component
---------

The system under test is divided into various components that each implement a part of its functionality.
These components appear to run in their own processes, and communicate with each other through message passing across a variety of sockets.
Component identifiers can be extracted from messages that explicity mention them, and the identifiers are **usually** postfixed with 'component'.


Log record
----------

The general structure of a log record seems to be the following::

    HEADER                                                                                                                   BODY
    ------------------------------------------------------------------------------------------------------------------------|----------------------
    <TIMESTAMP>                 <PROCESS NAME/ID> <EVENT TYPE> <TESTCASE FILE>:<TESTCASE LINE>(<SCOPE IN TESTCASE FILE>)     <RECORD CONTENT>
    =========================== ================= ============ ============================================================= ======================
    2014/Oct/24 19:16:48.062933 111               SYSCALL      ExampleComponentTest.ttcn:313(function:ExampleTestedFunction) open(0x7F323232) = -1

The `body` of the log record may contain newlines,
so a parser should always look for a timestamp right at the beginning of the line to identify the beginning of a new log record.


Structured data
---------------

Some log records contain structured data in their `body`.
These objects are represented in TTCN object notation format, and are often surrounded by other content.
Sadly, the various object structures do not appear to have anything in common besides the TTCN notation.


Messages
--------

Some of the aforementioned objects represent messages that were sent or received by components.
These messages have a source and a destination, unlike "log messages", which are our data source.
To avoid confusion, entries in the log should be referred to as either `log records` or `log entries`,
rather than messages.
