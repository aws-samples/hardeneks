#!/bin/sh
NAMESPACE=test-namespace
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
TESTS_DATA_DIRECTORY="$SCRIPT_DIR/../tests/data"
SINGLE_DIR=$1

process_directory() {
  DIR=$1
  mkdir -p "$DIR/cluster"

  if [ -f "$DIR/good.yaml" ] || [ -f "$DIR/bad.yaml" ]; then
    FILES=""
    [ -f "$DIR/good.yaml" ] && FILES="$FILES -f $DIR/good.yaml"
    [ -f "$DIR/bad.yaml" ] && FILES="$FILES -f $DIR/bad.yaml"

    kubectl apply $FILES
    
    kubectl get $FILES -o json | \
      jq -r '(.items // [.]) | .[].kind' | sort -u | while read kind; do
        filename=$(echo "${kind}" | tr '[:upper:]' '[:lower:]')_api_response.json
        kubectl get $FILES -o json | \
          jq --arg kind "$kind" '{items: [(.items // [.]) | .[] | select(.kind == $kind)]} | .kind = ($kind + "List")' > "$DIR/cluster/$filename"
      done
    
    kubectl delete $FILES
  fi
}

kubectl create namespace $NAMESPACE

if [ -n "$SINGLE_DIR" ] && [ -d "$SINGLE_DIR" ]; then
  process_directory "$SINGLE_DIR"
else
  for TEST_DIR in "$TESTS_DATA_DIRECTORY"/*; do
    echo "\nTest: $(basename "$TEST_DIR")"
    if [ -d "$TEST_DIR" ]; then
      process_directory "$TEST_DIR"
    fi
  done
fi

kubectl delete namespace $NAMESPACE --force