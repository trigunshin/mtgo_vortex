# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.define :local do |local|
    local.vm.box = "lucid64"
    local.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-server-10044-x64-vbox4210.box"
    local.vm.provider "virtualbox" do |v|
      v.customize [
                   "modifyvm", :id,
                   "--memory", "2048",
                   "--cpus",   "3"
                   ]
    end
    config.vm.provision :shell, :path => 'puppet-modules.sh'
    
    config.vm.provision :puppet do |puppet|
        #puppet.options = '--verbose --debug'
        #puppet.manifest_file = 'node.pp'
    end
    # apt cache - skip bunch of downloads if ever need to recreate
    config.vm.synced_folder 'apt-cache', '/var/cache/apt/archives'
    config.vm.network :forwarded_port, guest: 5000, host: 5000
    config.vm.synced_folder "src/", "/home/vagrant/mtgo_vortex"
  end

  config.vm.define :remotemtgovortex do |remotemtgovortex|
    remotemtgovortex.ssh.private_key_path = '~/.ssh/id_rsa'
    remotemtgovortex.vm.box = 'digital_ocean'
    remotemtgovortex.ssh.username = 'vagrant'
    remotemtgovortex.vm.provider :digital_ocean do |provider|
      provider.client_id = ''
      provider.api_key = ''
      provider.image = 'Ubuntu 12.10 x64'
    end
    remotemtgovortex.vm.synced_folder "src/", "/home/vagrant/mtgo_vortex"
    
    remotemtgovortex.vm.provision :shell, :path => 'puppet-modules.sh'
    remotemtgovortex.vm.provision :puppet do |puppet|
      #puppet.options = '--verbose --debug'
    end
  end

  # apt cache - skip bunch of downloads if ever need to recreate
  #config.vm.synced_folder 'apt-cache', '/var/cache/apt/archives'
  config.vm.network :forwarded_port, guest: 5000, host: 5000
  config.vm.synced_folder "src/", "/home/vagrant/mtgo_vortex"
end
