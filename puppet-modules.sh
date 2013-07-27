#!/bin/sh -e
if ! puppet module list | grep -q puppetlabs-nodejs; then
    puppet module install puppetlabs-nodejs
fi
if ! puppet module list | grep -q stdlib; then
    puppet module install puppetlabs/stdlib
fi
cd ~
wget "http://apt.puppetlabs.com/puppetlabs-release-quantal.deb"
dpkg -i "puppetlabs-release-quantal.deb"
sudo apt-get update -y
sudo apt-get install puppet-common