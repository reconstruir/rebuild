

from rebuild.package.package_db import package_db as DB
from rebuild.package.package_db_entry import package_db_entry as PE
from bes.build.build_system import build_system
from bes.build.build_target import build_target
from bes.build.package_descriptor import package_descriptor
from bes.build.requirement import requirement as R
from bes.build.requirement_list import requirement_list as RL
from bes.fs.file_checksum import file_checksum_list
from bes.fs.temp_file import temp_file
from bes.debug.debug_timer import debug_timer

db = DB('foo.sqlite')

TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = build_system.ALL)
TEST_FILES = file_checksum_list([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }
kiwi = PE('kiwi', '6.7.8', 2, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)
apple = PE('apple', '1.2.3', 0, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)

if db.has_package('kiwi'):
  db.remove_package('kiwi')

if db.has_package('apple'):
  db.remove_package('apple')
  
db.add_package(apple)
db.add_package(kiwi)

for x in db.list_all_descriptors():
  print('DESC: %s' % (str(x)))

print('has: %s' % (db.has_package('kiwi')))
print('has: %s' % (db.has_package('poto')))

t = debug_timer('x', level = 'error')

if True:
  for i in range(1, 1001):
    name = 'n%s' % (i)
    version = '1.0.0'
    files = file_checksum_list([ ( 'lib/libfoo%s.a' % (i), 'c1' ), ( 'include/libfoo%s.h' % (i), 'c2' ) ])
    p = PE(name, version, 0, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, files)
    db.add_package(p)

  t.start('%s: list_all()')
  db.list_all()
  t.stop()

t.start('%s: names()')
names = db.names()
print(len(names))
for name in names:
  #p = db.find_package(name)
  files = db.package_files(name)
  #print('%s: %s' % (name, files))
t.stop()
