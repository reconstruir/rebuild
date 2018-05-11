import unittest

class reb_foo_test(unittest.TestCase):

  def test_foo_func1(self):
    import foo
    self.assertEqual( 20, foo.foo_func1(10) )

if __name__ == '__main__':
  unittest.main()
