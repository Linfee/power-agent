#!/usr/bin/env bash
# Human-in-the-loop observation template, adapted from mattpocock/skills.
# Copy to a private temporary location and edit the two prompts for this case.
# Run in an interactive terminal: bash /path/to/copied-template.sh
# Both prompts time out after 300 seconds. Output contains the observation;
# do not enter passwords, tokens, personal data, or unredacted sensitive output.
# Sign-in or other sensitive actions remain in the user's own interface.
set -eu

printf '%s\n' 'Perform the agreed reproduction action, then press Enter.' >&2
if ! IFS= read -r -t 300 _; then
  printf '%s\n' 'No confirmation before timeout or input closed.' >&2
  exit 1
fi

printf '%s\n' 'Describe the observed result without secrets or personal data:' >&2
if ! IFS= read -r -t 300 observation; then
  printf '%s\n' 'No observation before timeout or input closed.' >&2
  exit 1
fi
printf 'Observation: %s\n' "$observation"
