#!/bin/bash
export LANG=C

echo "Cleaning zypper log"
[ -e /var/log/zypper.log ] && echo -n > /var/log/zypper.log

echo "Clearing unique ids"
rm -fv /var/lib/dbus/machine-id
rm -fv /var/lib/zypp/AnonymousUniqueId

echo "Rebuilding rpm database"
rpm --rebuilddb

echo "Cleaning kiwi files in image"
rm -rfv /etc/ImageVersion
rm -rfv /base-system
rm -rfv /var/cache/kiwi
rm -rfv /var/lib/dpkg

exit 0
