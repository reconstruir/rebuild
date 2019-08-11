#!/bin/bash

set -e

#config=$(pwd)/git.besfs
config=$(pwd)/pcloud.besfs
#config=$(pwd)/local.besfs

#export BESFS_CONFIG=$(pwd)/git.besfs

d=/tmp/git
rm -rf $d
mkdir -p $d

bes_fs.py -c $config ${1+"$@"}

clone_dir=$d/clone/git\@gitlab.com_rebuilder_test_lfs.git

#( cd $clone_dir && echo STATUS && git st )
#( cd $clone_dir && echo CHERRY && git cherry -v )

