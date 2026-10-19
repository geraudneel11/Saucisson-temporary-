#!/usr/bin/env bash
set -e
source .buildenv/bin/activate

cat > pyi_rth_cwd.py <<'PY'
import os
import sys
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)
PY

DATA_ARGS=()
while IFS= read -r -d '' file; do
    DATA_ARGS+=(--add-data "$file:.")
done < <(find . -maxdepth 1 -type f \
    ! -name '*.py' ! -name '*.sh' ! -name '*.spec' \
    ! -name '*.md' ! -name 'README*' -print0)

pyinstaller --noconfirm --clean --onefile \
    --name Pixsouls \
    --collect-all pygame \
    --runtime-hook ./pyi_rth_cwd.py \
    "${DATA_ARGS[@]}" main.py
