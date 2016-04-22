#!/bin/bash
# Build project in manylinux docker container
# Uses variables
#   PYTHON_VERSION : required : e.g. "2.7"
#   UNICODE_WIDTH : optional : "16" | "32" | "", defaults to 32
#   BUILD_DEPENDS : optional : string giving pip dependencies for build

set -e

function lex_ver {
    # Echoes dot-separated version string padded with zeros
    # Thus:
    # 3.2.1 -> 003002001
    # 3     -> 003000000
    echo $1 | awk -F "." '{printf "%03d%03d%03d", $1, $2, $3}'
}

function cpython_path {
    # Return path to cpython given
    # * version (of form "2.7")
    # * u_width ("16" or "32" default "32")
    #
    # For back-compatibility "u" as u_width also means "32"
    local py_ver="${1:-2.7}"
    local u_width="${2:-${UNICODE_WIDTH}}"
    local u_suff=u
    # Back-compatibility
    if [ "$u_width" == "u" ]; then u_width=32; fi
    # For Python >= 3.3, "u" suffix not meaningful
    if [ $(lex_ver $py_ver) -ge $(lex_ver 3.3) ] ||
        [ "$u_width" == "16" ]; then
        u_suff=""
    elif [ "$u_width" != "32" ]; then
        echo "Incorrect u_width value $u_width"
        # exit 1
    fi
    local no_dots=$(echo $py_ver | sed "s/\.//g")
    echo "/opt/python/cp${no_dots}-cp${no_dots}m${u_suff}"
}

function repair_wheelhouse {
    local in_dir=$1
    local out_dir=$2
    for whl in $in_dir/*.whl; do
        if [[ $whl == *none-any.whl ]]; then
            cp $whl $out_dir
        else
            auditwheel repair $whl -w $out_dir/
        fi
    done
    chmod -R a+rwX $out_dir
}

cd /io
export PATH="$(cpython_path $PYTHON_VERSION $UNICODE_WIDTH)/bin:$PATH"
if [ -n "$BUILD_DEPENDS" ]; then pip install $BUILD_DEPENDS; fi
pip wheel --no-deps -w /unfixed_wheels .
mkdir -p dist
repair_wheelhouse /unfixed_wheels dist
