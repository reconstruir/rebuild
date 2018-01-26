#!/bin/bash

#set -e

files="fructose-3.4.5.tar.gz \
mercury-1.2.8.tar.gz \
arsenic-1.2.9.tar.gz \
fiber-1.0.0.tar.gz \
pear-1.2.3.tar.gz \
orange-6.5.4.tar.gz \
"

tmp_dir=/tmp/make_pc_files.$$
rm -rf $tmp_dir
mkdir -p $tmp_dir

source_dir=$tmp_dir/source
mkdir -p $source_dir

prefix_dir=$tmp_dir/prefix
mkdir -p $prefix_dir

log_dir=$tmp_dir/log
mkdir -p $log_dir

pkg_config_dir=$prefix_dir/lib/pkgconfig
mkdir -p $pkg_config_dir

echo "source_dir: $source_dir"
echo "prefix_dir: $prefix_dir"
echo "   log_dir: $log_dir"

export PATH=$PATH:~/x/files/bin
export PKG_CONFIG_PATH=$pkg_config_dir

for tarball in $files; do
  name=$(echo $tarball | sed 's/.tar.gz//')
  log=$log_dir/$name.log
  echo "building: $name"
  tar xf $tarball -C $source_dir
  ( cd $source_dir/$name && ./configure --prefix=$prefix_dir && make && make install ) >& $log
  rv=$?
  if [ $rv != 0 ]; then
    echo "failed to build: $name.  log: $log"
    tail -20 $log
  fi
done

exit 0
