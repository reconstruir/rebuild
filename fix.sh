#!/bin/sh

rh=~/proj/rehack/bin/rehack.sh

function _fix()
{
  ${rh} refactor rename "$@" lib tests bin
}

_fix bes.shell_framework bat.shell_framework
_fix "from bes.files.bf_checksum import file_checksum_list" "from bes.fs.file_checksum import file_checksum_list"
_fix "from bes.files.bf_checksum import file_checksum" "from bes.fs.file_checksum import file_checksum"
_fix "from bes.system.compat import with_metaclass" ""
_fix "bes.fs.file_path import file_path" "bes.files.bf_path import bf_path"
_fix "file_path." "bf_path."

