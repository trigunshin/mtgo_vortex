include nodejs

file { '/usr/etc':
    ensure => 'directory',
}

file { '/usr/etc/npmrc':
    ensure => 'present',
    content => 'cache=/vagrant/npm-cache',
    require => File['/usr/etc'],
}

File['/usr/etc/npmrc'] -> Package <| |>

package { 'mimosa':
    ensure => 'installed',
    provider => 'npm',
    require => Package['npm'],
}