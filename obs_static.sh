#!/bin/bash

mkdir -p obs

for image_system in images/*;do
    system=$(basename "${image_system}")
    mkdir -p obs/"${system}"
    cp -a "${image_system}"/* obs/"${system}"/
    for image in obs/"${system}"/*;do
        if [ -d "${image}/root" ];then
            pushd "${image}/root"
            find -type d | xargs chmod 0755
            chkstat --system --root "$(pwd)" --set
            tar -czf ../root.tar.gz *
            popd
            sudo rm -rf "${image}/root"
        fi
    done
done
