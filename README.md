pyiwa
=====

Read iWork's internal iwa format using python.

pyiwa was written as a recovery tool for ugly disk crashes or accidental deletions. It is not a .pages file parser.

Actually, there's no such thing as a iWork '09+ pages file. They are directories containing another directory and a zip file which contains the actual, useful payload.

This payload is constituted of iwa files. They were reverse-engineered by @obriensp (see: https://github.com/obriensp/iWorkFileFormat).

pyiwa reads iwa files extracted from iWork zips.

First it extracts the hacked-upon-snappy compressed stream that an iwa file actually is.

Then it uses introspection to parse the various contatenated fields and stores them in a list of Protocol buffers (actually an array of them). The reverse engineering is not complete so some fields are just not understood and skipped. There is no way to match them with a known protocol buffer so we ignore them.

Once all the fields have been listed, another loop searches for fields containing a text item and prints the text items.

Therefore pyiwa could be considered, as it is, as an iwacat.

However there's more to it as one could use it to parse the formatting, fonts, etc. used to make it an iwa2*, though I doubt it's worth it.

It's also a good programming exercise in python with binary streams.
