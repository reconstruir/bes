
if [ -n "$_BES_TRACE" ]; then echo "bes_caca.sh begin"; fi

function bes_caca_print()
{
  echo foo
  return 0
}


if [ -n "$_BES_TRACE" ]; then echo "bes_caca.sh end"; fi
