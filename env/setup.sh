rebuild-dev-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild-dev-go()
{
  cd $(rebuild-dev-root)
  return 0
}

rebuild-dev-setup()
{
  bes-dev-setup
  bes-setup $(rebuild-dev-root)
  return 0
}
