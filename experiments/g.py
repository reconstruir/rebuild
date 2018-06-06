
import difflib

a = ['/usr/bin', '/bin', '/usr/sbin', '/sbin', '/Users/ramiro/proj/bes/bin', '/Users/ramiro/proj/rebuild/bin']
b = ['/a/bin', '/usr/bin', '/bin', '/usr/sbin', '/Users/ramiro/proj/bes/bin', '/Users/ramiro/proj/rebuild/bin', '/b/bin']

s = difflib.SequenceMatcher(isjunk = None, a = a, b = b)

for tag, i1, i2, j1, j2 in s.get_opcodes():
  print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)" % (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2]))
