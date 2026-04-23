#!/bin/bash
DB_PATH="/home/bdkl/docs/Calibre Library/metadata.db"
export PYTHONPATH=src

queries=(
  "tags:Fic"
  "tags:\"=Fic.Fantasy\""
  "tags:Fic AND tags:Fantasy"
  "tags:Fic tags:Fantasy"
  "tags:Fic OR tags:NonFic"
  "NOT tags:Fic"
  "(tags:Fic OR tags:NonFic) AND NOT tags:Gaming"
  "vl:\"The Tabletop\""
  "tags:Fic and (not tags:Horror) and tags:\"=Fic.SciFi.Cyberpunk\""
)

for q in "${queries[@]}"; do
  echo "Testing: $q"
  python -m cquarry --search "$q" --db "$DB_PATH" --output /tmp/query_test.txt --quiet
  if [ $? -ne 0 ]; then
    echo "FAILED SYNTAX: $q"
    exit 1
  fi
  head -n 2 /tmp/query_test.txt | grep "Matches" || echo "No matches (but syntax OK)"
  echo "---"
done
echo "All syntax tests passed."
