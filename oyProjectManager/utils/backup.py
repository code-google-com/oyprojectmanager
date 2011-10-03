///
The backup script for the system.

It accepts a ``project`` and ``sequence`` name and an ``output_path`` which is
the output of the filtered files.

The system creates filter rules to be used with ``rsync`` command and then calls
the ``rsync`` command on the server.

:arg project: The name of the project. It should match the exact project name
  otherwise it will raise a ValueError.

:arg sequence: The name of the sequence. It should match the exact sequence
  name, and if skipped, all the sequences under the given project will be
  filtered and backed up.

:arg filter_rules: extra filter rules for custom filters. Can be skipped.
///



