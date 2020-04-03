#!/bin/bash

mkdir -p obs

for image_system in images/*;do
    system=$(basename "${image_system}")
    mkdir -p obs/"${system}"
    cp -a "${image_system}"/* obs/"${system}"/
    for image in obs/"${system}"/*;do
        if [ -d "${image}/root" ];then
            pushd "${image}/root"
            sudo chown -R root:root .
            tar -czf ../root.tar.gz *
            popd
            sudo rm -rf "${image}/root"
        fi
    done
done
