#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

function _bes_all_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

source $(_bes_all_this_dir)/bes_shell.bash
source $(_bes_all_this_dir)/bes_git.bash
source $(_bes_all_this_dir)/bes_git_subtree.bash
source $(_bes_all_this_dir)/bes_download.bash
source $(_bes_all_this_dir)/bes_bfg.bash
source $(_bes_all_this_dir)/bes_version.bash
source $(_bes_all_this_dir)/bes_python.bash
