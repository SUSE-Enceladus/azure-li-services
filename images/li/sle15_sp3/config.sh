#!/bin/bash
#================
# FILE          : config.sh
#----------------
# PROJECT       : OpenSuSE KIWI Image System
# COPYRIGHT     : (c) 2018 SUSE LINUX Products GmbH. All rights reserved
#               :
# AUTHOR        : Marcus Schaefer <ms@suse.de>
#               :
# BELONGS TO    : Operating System images
#               :
# DESCRIPTION   : configuration script for SUSE based
#               : operating systems
#               :
#               :
# STATUS        : BETA
#----------------
#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig
test -f /.profile && . /.profile

#======================================
# Greeting...
#--------------------------------------
echo "Configure image: [$kiwi_iname]..."

#======================================
# Setup base product
#--------------------------------------
pushd /etc/products.d
ln -sf SLES_SAP.prod baseproduct
popd

#=========================================
# Set sysconfig options
#-----------------------------------------
baseUpdateSysConfig /etc/sysconfig/bootloader LOADER_TYPE grub2
baseUpdateSysConfig /etc/sysconfig/keyboard COMPOSETABLE "clear latin1.add"
baseUpdateSysConfig /etc/sysconfig/language INSTALLED_LANGUAGES ""
baseUpdateSysConfig /etc/sysconfig/language RC_LANG "C.UTF-8"
baseUpdateSysConfig /etc/sysconfig/network/dhcp DHCLIENT_SET_HOSTNAME yes
baseUpdateSysConfig /etc/sysconfig/network/dhcp WRITE_HOSTNAME_TO_HOSTS no
baseUpdateSysConfig /etc/sysconfig/security POLKIT_DEFAULT_PRIVS restrictive
baseUpdateSysConfig /etc/sysconfig/windowmanager DEFAULT_WM ""
baseUpdateSysConfig /etc/sysconfig/windowmanager INSTALL_DESKTOP_EXTENSIONS no

#=========================================
# Allow unsupported modules
#-----------------------------------------
if [ -f /etc/modprobe.d/unsupported-modules ];then
    sed -i -r -e 's/^(allow_unsupported_modules[[:space:]]*).*/\10/' \
        /etc/modprobe.d/unsupported-modules
fi

# Set sysconfig for things that are not setup by default, net new
echo 'CONSOLE_FONT="lat9w-16.psfu"' >> /etc/sysconfig/console
echo 'CONSOLE_SCREENMAP="trivial"' >> /etc/sysconfig/console
echo 'HWCLOCK="-u"' >> /etc/sysconfig/clock
echo 'UTC=true' >> /etc/sysconfig/clock

# Configuration outside of sysconfig
# Setup policy kit
[ -x /sbin/set_polkit_default_privs ] && /sbin/set_polkit_default_privs

# ssh settings are different than public Azure per Msft request
# Set sshd keep alive interval
sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 180/' \
    /etc/ssh/sshd_config

# Remove the password for root
# Note the string matches the password set in the config file
sed -i 's/^root:[^:]:/root::/' /etc/shadow

#=========================================
# File limits
#-----------------------------------------
echo >> /etc/security/limits.conf
echo "* soft nofile 32768" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

#=========================================
# Module for sunrpc
#=========================================
echo >> /etc/modprobe.d/sunrpc.conf
echo "options sunrpc tcp_max_slot_table_entries=128" >> /etc/modprobe.d/sunrpc.conf

#=========================================
# Disable default targetpw directive
#-----------------------------------------
sed -i -e '/^Defaults targetpw/,/^$/ s/^/#/' \
    /etc/sudoers

#=========================================
# Set NFS verbosity per Msft request
#-----------------------------------------
sed -i 's/Verbosity\ =\ 0/Verbosity\ =\ 3/' /etc/idmapd.conf

# Track the variant
echo 'VARIANT_ID="sles-sap"' >> /etc/os-release

#======================================
# Create service trigger files
#--------------------------------------
touch /.azure-li-config-lookup.trigger
touch /.azure-li-network.trigger
touch /.azure-li-user.trigger
touch /.azure-li-install.trigger
touch /.azure-li-call.trigger
touch /.azure-li-storage.trigger
touch /.azure-li-machine-constraints.trigger
touch /.azure-li-system-setup.trigger
touch /.azure-li-report.trigger
touch /.azure-li-cleanup.trigger

#======================================
# Activate azure Li/VLi services
#--------------------------------------
suseInsertService azure-li-config-lookup
suseInsertService azure-li-network
suseInsertService azure-li-user
suseInsertService azure-li-install
suseInsertService azure-li-call
suseInsertService azure-li-storage
suseInsertService azure-li-machine-constraints
suseInsertService azure-li-system-setup
suseInsertService azure-li-report
suseInsertService azure-li-cleanup

#======================================
# Activate system services
#--------------------------------------
suseInsertService rc-local
suseInsertService sshd
suseInsertService multipathd
suseInsertService kdump
suseRemoveService nscd

#======================================
# Setup default target, multi-user
#--------------------------------------
baseSetRunlevel 3
