file { '/home/vagrant/.ssh':
    ensure => 'directory',
    mode => 0700,
    owner => 'vagrant',
    group => 'vagrant',
}

file { '/home/vagrant/.ssh/id_rsa':
    source  => '/tmp/vagrant-puppet/manifests/ssh/id_rsa',
    mode => 0600,
    owner => 'vagrant',
    group => 'vagrant',
}

file { '/home/vagrant/.ssh/id_rsa.pub':
    source  => '/tmp/vagrant-puppet/manifests/ssh/id_rsa.pub',
    mode => 0600,
    owner => 'vagrant',
    group => 'vagrant',
}

sshkey { 'github':
    ensure => 'present',
    name => 'github.com',
    # host_aliases => [],
    type => 'ssh-rsa',
    key => 'AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ=='
}

file { '/etc/ssh/ssh_known_hosts':
    mode => 0644,
}
