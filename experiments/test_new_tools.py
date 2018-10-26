#!/usr/bin/env python

from rebuild.package import artifact_manager
from rebuild.tools_manager import new_tools_manager
from rebuild.base import build_target, build_version, package_descriptor
from rebuild.package.fake_package_unit_test import fake_package_unit_test as FPUT

def main():
  bt = build_target.make_host_build_target()
  mutations = bt.to_dict()
  del mutations['build_path']
  am = FPUT.make_artifact_manager(debug = False, recipes = FPUT.TEST_RECIPES, build_target = bt,
                                  mutations = mutations)
  wanted =  [
    package_descriptor('orange_juice', '1.4.5'),
    package_descriptor('smoothie', '1.0.0'),
   ]
  
  tm = new_tools_manager('/tmp/new_tools', am)
  tm.ensure_tools(wanted)
  tm.ensure_tools(wanted)

if __name__ == '__main__':
  main()
