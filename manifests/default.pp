import "ssh.pp"
import "system-packages.pp"
import "mongo.pp"
import "node.pp"
import "redis.pp"

########################################################################

file { '/home/vagrant/info-sequences':
    ensure => 'directory',
    mode => 0775,
    owner => 'vagrant',
    group => 'vagrant',
}

########################################################################

$install_dir = '/home/vagrant'

#exec { "info-sequences-checkout":
#    cwd => $install_dir,
#    command => '/usr/bin/git clone git@github.com:trigunshin/info-sequences.git',
#    creates => "${install_dir}/info-sequences",
#    unless => '/usr/bin/test -d info-sequences',
#    user => 'vagrant',
#    require => [Package['git-core']],
#}

file { '/home/vagrant/.screenrc':
   ensure => 'link',
   target => '/vagrant/.screenrc',
}

exec { "load-screen":
    cwd => "$install_dir/info-sequences",
    command => '/usr/bin/screen -AmdS infoseq -t appjs bash',
    user => 'vagrant',
    unless => "/usr/bin/test 1 '!=' `ps aux|grep screen|wc -l`",
    require => [
        File['/home/vagrant/.screenrc'],
        Package['screen'],
        Class['nodejs'],
        #Exec['info-sequences-checkout'],
    ],
}

exec { "run-app":
    cwd => "$install_dir/info-sequences",
    command => "/usr/bin/screen -S infoseq -p appjs -X stuff \'node app.js\r\'",
    user => 'vagrant',
    require => [
        Exec['load-screen'],
    ],
}