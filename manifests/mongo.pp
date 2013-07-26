exec { 'add-mongo-apt':
    command => '/bin/echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" > /etc/apt/sources.list.d/10gen.list',
    unless => '/bin/grep downloads-distro.mongodb.org /etc/apt/sources.list.d/10gen.list',
    before => Exec['apt-get-update'],
}

exec { 'add-mongo-apt-key':
    command => '/usr/bin/apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10',
    unless => '/usr/bin/apt-key list | /bin/grep 7F0CEB10',
    before => Exec['apt-get-update'],
}

package { 'mongodb-10gen':
    ensure => 'installed',
    require => [Exec['add-mongo-apt-key'], Exec['add-mongo-apt']],
    #notify => Service['mongodb']
}
