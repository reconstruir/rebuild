rebuild-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild-go()
{
  cd $(rebuild-root)
  return 0
}

rebuild-setup()
{
  bes-setup
  bes-setup-dir $(rebuild-root)
  return 0
}
