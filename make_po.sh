declare -a langs=("en" "ru")

for lang in "${langs[@]}"
do
  touch new.po
  find . -type f -iname "*.py" -not -path "./venv/*"  | xgettext -L python -o new.po -j -f -
  cp locale/${lang}/LC_MESSAGES/messages.po old.po
  msgmerge -N old.po new.po > locale/${lang}/LC_MESSAGES/messages.po
  rm new.po
  rm old.po
  msgfmt locale/${lang}/LC_MESSAGES/messages.po -o locale/${lang}/LC_MESSAGES/messages.mo
done
