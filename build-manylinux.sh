#!/bin/bash
set -euo pipefail

# ================= CONFIG =================
PYTHON_VERSION="3.14.3"
PYTHON_SHORT="3.14"
PY_PREFIX="/opt/python-custom/${PYTHON_VERSION}"
WORKDIR="/work"
# ========================================

echo "=== Installing Python ${PYTHON_VERSION} (shared) in ${PY_PREFIX} ==="

# Install deps (manylinux_2_28 uses dnf)
dnf install -y \
    wget gcc make openssl-devel bzip2-devel libffi-devel \
    zlib-devel xz-devel sqlite-devel ncurses-devel readline-devel tk-devel

# Build Python
cd /tmp
wget -q https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
tar -xzf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}

./configure \
    --prefix="${PY_PREFIX}" \
    --enable-shared \
    --with-ensurepip=install

make -j$(nproc)
make altinstall

# Setup runtime lib path
export LD_LIBRARY_PATH="${PY_PREFIX}/lib:$LD_LIBRARY_PATH"

# Create helper symlinks (no overwrite system python)
ln -sf "${PY_PREFIX}/bin/python${PYTHON_SHORT}" /usr/local/bin/python314
ln -sf "${PY_PREFIX}/bin/pip${PYTHON_SHORT}" /usr/local/bin/pip314

# Verify shared lib
if ! ldd "${PY_PREFIX}/bin/python${PYTHON_SHORT}" | grep -q libpython; then
    echo "ERROR: libpython shared library missing"
    exit 1
fi

echo "=== Python ${PYTHON_VERSION} installed OK ==="

# ================= VENV =================
cd "${WORKDIR}"

echo "=== Creating virtualenv ==="
/usr/local/bin/python314 -m venv venv
source venv/bin/activate

echo "=== Installing deps ==="
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt pyinstaller

# Ensure PyInstaller finds libpython
export LD_LIBRARY_PATH="$(python -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))'):$LD_LIBRARY_PATH"

# ================= BUILD =================
chmod +x build.sh
bash build.sh

echo "=== BUILD COMPLETE ==="
