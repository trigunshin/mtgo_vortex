package { 'redis-server':
    ensure => 'installed',
    before => File['/etc/redis/redis.conf'],
}

file { '/etc/redis/redis.conf':
  ensure => present
}->
file_line { 'redis_memory_size':
  line => 'maxmemory 64mb',
  path => '/etc/redis/redis.conf',
}
service { 'redis-server':
  ensure     => running,
  enable     => true,
  subscribe  => File['/etc/redis/redis.conf'],
}