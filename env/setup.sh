rebuild-dev-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild-go()
{
  cd $(rebuild-dev-root)
  return 0
}

rebuild-dev()
{
  bes-dev
  bes-setup $(rebuild-dev-root)
  rebuild-go
  return 0
}
