file { "apt-cache-partial":
    ensure => "directory",
    owner  => "root",
    group  => "root",
    mode   => 755,
    path   => "/var/cache/apt/archives/partial",
}

exec { 'apt-get-update':
    command => '/usr/bin/apt-get update',
    require => [File["apt-cache-partial"],],
}

# run apt-get update before package installs
Exec['apt-get-update'] -> Package <| |>

package { 'unzip':
    ensure => 'installed'
}
package { 'screen':
    ensure => 'installed'
}
package { 'git-core':
    ensure => 'installed'
}
package { 'curl':
    ensure => 'installed'
}
package { 'libxslt1-dev':
    ensure => 'installed'
}