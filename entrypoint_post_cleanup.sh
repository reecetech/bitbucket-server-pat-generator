#!/bin/bash

# Don't fail on error. Cleanup is best effort
pat_id=${STATE_CLEANUP_PAT_ID} python /app/pat_helper.py revoke || true
