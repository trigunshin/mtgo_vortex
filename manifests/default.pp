import "ssh.pp"
import "system-packages.pp"
import "mongo.pp"
#import "node.pp"
import "redis.pp"
include java

########################################################################

package { 'argparse':
    ensure => 'installed',
    provider => 'pip',
    require => Package['python-pip'],
}
package { 'pymongo':
    ensure => 'installed',
    provider => 'pip',
    require => Package['python-pip'],
}

########################################################################

$install_dir = '/home/vagrant'

cron { data_fetch:
  command => "/usr/bin/python $install_dir/mtgo_vortex/prices.py",
  user    => vagrant,
  hour    => [1, 13],
  minute  => 0,
  require => [Package['pymongo'],Package['argparse'],Package['mongodb-10gen']]
}

file { '/home/vagrant/.screenrc':
   ensure => 'link',
   target => '/vagrant/.screenrc',
}

exec { "load-screen":
    cwd => "$install_dir/mtgo_vortex",
    command => '/usr/bin/screen -AmdS mtgo -t appjs bash',
    user => 'vagrant',
    unless => "/usr/bin/test `screen -list | grep mtgo | wc -l` '-gt' 0",
    require => [
        File['/home/vagrant/.screenrc'],
        Package['screen'],
    ],
}
exec { "first-price-fetch":
    cwd => "$install_dir/mtgo_vortex",
    command => "/usr/bin/screen -S mtgo -p appjs -X stuff \'python prices.py\r\'",
    user => 'vagrant',
    require => [
        Exec['load-screen'],
        Cron['data_fetch'],
    ],
}
