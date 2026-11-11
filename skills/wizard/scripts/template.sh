#!/usr/bin/env bash
# Wizard template: author the STAGES section before use.
# No external service or environment file is changed unless authored stages
# explicitly call an appropriate helper and the operator confirms the target.
set +x
set -euo pipefail

TOTAL_STAGES=0
_STAGE_INDEX=0

banner() {
  printf '\n%s\n%s stage(s). Stop with Ctrl-C.\n\n' "$1" "$TOTAL_STAGES"
}

stage() {
  _STAGE_INDEX=$((_STAGE_INDEX + 1))
  printf '\nStage %s/%s: %s\n' "$_STAGE_INDEX" "$TOTAL_STAGES" "$1"
}

say() { printf '  %s\n' "$1"; }

# Print only public URLs, without credentials, tokens or private query strings.
show_url() { printf '  Open: %s\n' "$1"; }

# EOF and anything except y/yes are rejection, not approval.
confirm() {
  local reply=''
  printf '  %s [y/N] ' "$1" >&2
  IFS= read -r reply || return 1
  [[ "$reply" == [yY] || "$reply" == [yY][eE][sS] ]]
}

# Store input in WIZARD_VALUE_* variables, avoiding library-local collisions.
_valid_input_name() { [[ "$1" =~ ^WIZARD_VALUE_[A-Z0-9_]+$ ]]; }

ask() {
  local name="$1" prompt="$2" input=''
  _valid_input_name "$name" || { printf 'Invalid input variable name.\n' >&2; return 1; }
  printf '  %s ' "$prompt" >&2
  IFS= read -r input || { printf '\nInput ended; cancelled.\n' >&2; return 1; }
  [[ -n "$input" ]] || { printf 'Input cannot be empty.\n' >&2; return 1; }
  printf -v "$name" '%s' "$input"
}

# Secrets are accepted only from a terminal and are never shown or defaulted
# from an existing file. Do not enable shell tracing around this helper.
ask_secret() {
  local name="$1" prompt="$2" input=''
  _valid_input_name "$name" || { printf 'Invalid input variable name.\n' >&2; return 1; }
  [[ -t 0 ]] || { printf 'Secret input requires a terminal.\n' >&2; return 1; }
  input=$(
    local tty_state secret=''
    tty_state=$(stty -g <&0) || exit 1
    trap 'stty "$tty_state" <&0' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    stty -echo <&0 || exit 1
    printf '  %s ' "$prompt" >&2
    if ! IFS= read -r secret; then
      printf '\nSecret input ended; cancelled.\n' >&2
      exit 1
    fi
    printf '\n' >&2
    [[ -n "$secret" ]] || { printf 'Secret cannot be empty.\n' >&2; exit 1; }
    printf '%s' "$secret"
  ) || return 1
  printf -v "$name" '%s' "$input"
}

# write_env FILE KEY VALUE: idempotent for simple unquoted dotenv assignments.
# Reject ambiguous syntax rather than change its meaning. Writes are explicitly
# confirmed, use a same-directory private temporary file and replace the target;
# resulting permissions are 0600. Concurrent writers require external control.
# Do not invoke for a secret unless that exact file write is authorized.
write_env() (
  local file="$1" key="$2" value="$3" tmp='' line count=0 failed=0
  _cleanup_env_tmp() {
    if [[ -n "$tmp" ]]; then
      rm -f -- "$tmp"
    fi
  }
  trap _cleanup_env_tmp EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || { printf 'Invalid environment key.\n' >&2; return 1; }
  [[ "$value" =~ ^[A-Za-z0-9_./:@%+=,-]+$ ]] || { printf 'Unsupported dotenv value; use a project-specific safe writer.\n' >&2; return 1; }
  [[ ! -L "$file" ]] || { printf 'Refusing symlink target.\n' >&2; return 1; }
  if [[ -e "$file" && ! -f "$file" ]]; then
    printf 'Environment target is not a regular file.\n' >&2; return 1
  fi
  confirm "Write key $key to $file (file permissions become 0600)?" || {
    printf 'Environment write declined.\n' >&2; return 1
  }
  tmp=$(umask 077; mktemp "${file}.tmp.XXXXXXXX") || return 1
  if [[ -f "$file" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      if [[ "$line" =~ ^[[:space:]]*(export[[:space:]]+)?${key}[[:space:]]*= ]]; then
        if [[ ! "$line" =~ ^${key}=[A-Za-z0-9_./:@%+=,-]*$ ]] || (( count > 0 )); then failed=1; break; fi
        count=$((count + 1))
      elif [[ "$line" =~ ^[[:space:]]*$ || "$line" =~ ^[[:space:]]*# || "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*=[A-Za-z0-9_./:@%+=,-]*$ ]]; then
        printf '%s\n' "$line" >> "$tmp" || { failed=1; break; }
      else
        failed=1; break
      fi
    done < "$file" || failed=1
  fi
  if (( failed )); then
    printf 'Ambiguous or unreadable environment file; unchanged.\n' >&2
    return 1
  fi
  if ! printf '%s=%s\n' "$key" "$value" >> "$tmp" || ! mv -f -- "$tmp" "$file"; then
    printf 'Environment write failed.\n' >&2
    return 1
  fi
  tmp=''
  printf '  Wrote %s to %s.\n' "$key" "$file"
)

finish() { printf '\nCompleted the authored stages. Verify any outstanding manual steps.\n'; }

# STAGES: replace this guard with the actual, verified procedure. Set
# TOTAL_STAGES, then call banner, stage, the necessary helpers, and finish.
# External writes, permissions, and terms need their own exact authorization.
run_wizard() {
  printf 'Wizard has no authored stages; fill the STAGES section before use.\n' >&2
  return 2
}

run_wizard "$@"
