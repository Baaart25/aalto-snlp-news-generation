#!/bin/bash

CC_CORPUS_PATH="$2"
CC_CORPUS_SCRIPT_PATH=$CC_CORPUS_PATH/scripts
ALLOWED_MIMES_PATH=$CC_CORPUS_PATH/allowed_mimes.txt
CC_OUTPUT_PATH="$3"

while read -r LINE
do
  IFS='|' read -ra INDEX <<< "$LINE"

  SITE="${INDEX[0]}"
  URL="${INDEX[1]}"

  python "$CC_CORPUS_SCRIPT_PATH"/get_indexfiles.py \
    -t $URL \
    -o "$CC_OUTPUT_PATH/$SITE/cc_index/" \
    -c CC-MAIN-2021-31

  python "$CC_CORPUS_SCRIPT_PATH"/filter_index.py \
    "$CC_OUTPUT_PATH/$SITE/cc_index/" \
    "$CC_OUTPUT_PATH/$SITE/cc_index_filtered/" \
    -a "$ALLOWED_MIMES_PATH" \
    -P 12

  python "$CC_CORPUS_SCRIPT_PATH"/deduplicate_index_urls.py \
    -i "$CC_OUTPUT_PATH/$SITE/cc_index_filtered/" \
    -o "$CC_OUTPUT_PATH/$SITE/cc_index_dedup/"

  mkdir "$CC_OUTPUT_PATH/$SITE/temp"
  python "$CC_CORPUS_SCRIPT_PATH"/download_pages.py \
    "$CC_OUTPUT_PATH/$SITE/cc_index_dedup/*.gz" \
    "$CC_OUTPUT_PATH/$SITE/cc_index_output" \
    "$CC_OUTPUT_PATH/$SITE/cc_downloaded" \
    "$CC_OUTPUT_PATH/$SITE/error.txt" \
    -t "$CC_OUTPUT_PATH/$SITE/temp/" \
    -e warc.gz \
    -P 15

done < "$1"