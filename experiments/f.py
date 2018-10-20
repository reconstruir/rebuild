
from rebuild.package import artifact_manager
from rebuild.tools_manager import new_tools_manager
from rebuild.base import build_target, build_version, package_descriptor

def main():
  bt = build_target.make_host_build_target()
  am = artifact_manager('/home/ramiro/proj/third_party/BUILD/artifacts', no_git = True)

  wanted =  [
    package_descriptor('gnu_automake', '1.15'),
    package_descriptor('cython', '0.23.4'),
    package_descriptor('swig', '3.0.12'),
    package_descriptor('gnu_bison', '3.0.4'),
   ]
  
  tm = new_tools_manager('/tmp/coksuk', am)
  tm.ensure_tools(wanted)
  tm.ensure_tools(wanted)

if __name__ == '__main__':
  main()
