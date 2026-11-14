#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
${EXEC:-exec} "$SCRIPT_DIR/../../../repo.sh" etm -e omni.physics.ui "$@"
