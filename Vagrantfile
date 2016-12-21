# -*- mode: ruby -*-
Vagrant.configure('2') do |config|

#  https://github.com/mitchellh/vagrant/issues/1303
  config.ssh.forward_agent = true
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
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
    machine.vm.network "forwarded_port", guest: 9999, host: 8080
    machine.vm.hostname = 'hacs-dev.local'
$provision_script = <<SCRIPT
    set -x
    set -e
    echo "@TODO:: anything required before ansible, should be placed here!"

SCRIPT
    machine.vm.provision "shell",
        inline: $provision_script
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
