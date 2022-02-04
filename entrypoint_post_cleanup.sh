#!/bin/bash

# Don't fail on error. Cleanup is best effort
export PAT_ID=${_STATE_CLEANUP_PAT_ID}
python /app/pat_helper.py revoke || true
