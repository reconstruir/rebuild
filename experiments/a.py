

from rebuild.package.artifact_db import artifact_db as DB
from rebuild.package import package_metadata as MD, artifact_descriptor as AD
from rebuild.base import build_system, build_target, package_descriptor, requirement as R, requirement_list as RL
from bes.fs import file_checksum_list

db = DB('art.db')

TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = build_system.ALL)
TEST_FILES = file_checksum_list([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
TEST_FILES.sort()
TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

kiwi = MD('kiwi-6.7.8-2.tar.gz', 'kiwi', '6.7.8', 2, 0, 'macos', 'release', [ 'x86_64' ], '', TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES, 'chk1')
apple = MD('apple-1.2.3.tar.gz', 'apple', '1.2.3', 0, 0, 'macos', 'release', [ 'x86_64' ], '', TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES, 'chk1')

print(db.has_artifact(kiwi.artifact_descriptor))

db.add_artifact(apple)
db.add_artifact(kiwi)

print(db.has_artifact(kiwi.artifact_descriptor))
