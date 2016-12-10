# -*- mode: ruby -*-
Vagrant.configure('2') do |config|

  config.ssh.private_key_path = "~/.ssh/id_rsa"
  config.ssh.forward_agent = true
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/srv/hacs/"

  # Multi Machine pattern
  config.vm.define 'hacs-dev' do |machine|
    machine.vm.box = "ubuntu/xenial64"
    machine.vm.provider "virtualbox" do |vb|
        # Memory Needs
        vb.memory = 1024
    end
    machine.vm.network "private_network", ip: '192.168.10.10'
    machine.vm.network "forwarded_port", guest: 8080, host: 8080
    machine.vm.hostname = 'hacs-dev.local'
    machine.vm.provision 'ansible_local' do |ansible|
      ansible.playbook = 'playbook.yml'
      ansible.install = true
      ansible.install_mode = :default
      ansible.provisioning_path = "/srv/hacs/ansible/"
      ansible.inventory_path = "hosts"
      ansible.tmp_path = "/tmp/vagrant-ansible"
    end
  end
end
