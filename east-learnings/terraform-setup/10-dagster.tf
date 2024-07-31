# This is a Terraform configuration file that sets up a Dagster instance with a PostgreSQL database and a pgAdmin instance for managing the database.
# Note that variables and secrets are not here, those you would need to setup yourself.


resource "docker_network" "dagster_network" {
  name   = "dagster_network"
  driver = "bridge"
}

resource "docker_image" "dagster_user_code_image" {
  name = "dagster_user_code_image"
  build {
    context    = "${local.basepath}/dagster"
    dockerfile = "Dockerfile_user_code"
    build_arg = {
      BASE_PATH = "${abspath(local.basepath)}"
    }
  }
}

resource "docker_image" "dagster_dagster_image" {
  name         = "dagster_dagster_image"
  keep_locally = true
  build {
    context    = "${local.basepath}/dagster"
    dockerfile = "Dockerfile_dagster"
    build_arg = {
      BASE_PATH = "${abspath(local.basepath)}"
    }
  }


}

resource "docker_container" "dagster_postgresql" {
  image   = "postgres:11"
  name    = "dagster_postgresql"
  restart = "always"
  dns = [docker_container.dnsmasq_container.network_data[0].ip_address]

  env = [
    "POSTGRES_USER=dagster",
    "POSTGRES_PASSWORD=${local.decrypted_secrets["postgresql_password"]}",
    "POSTGRES_DB=dagster"
  ]

  networks_advanced {
    name = "${docker_network.east_network.name}"
    aliases = ["dagster_postgresql"]
  }

  volumes {
    host_path = abspath("${local.basepath}/_terraform/_data/postgresql")
    container_path = "/var/lib/postgresql/data"
  }

}

resource "docker_container" "pgadmin" {
  image   = "dpage/pgadmin4"
  name    = "pgadmin4_container"
  restart = "always"
  dns = [docker_container.dnsmasq_container.network_data[0].ip_address]

  ports {
    internal = 80
    external = 7070
  }

  env = [
    "PGADMIN_DEFAULT_EMAIL=dagster@east.fi",
    "PGADMIN_DEFAULT_PASSWORD=${local.decrypted_secrets["postgresql_password"]}"
  ]

  volumes {
    host_path = abspath("${local.basepath}/_terraform/_data/pgadmin")
    container_path = "/var/lib/pgadmin"
  }

  networks_advanced {
    name = "${docker_network.east_network.name}"
    aliases = ["pgadmin4"]
  }

}

resource "docker_container" "dagster_user_code" {
  image   = docker_image.dagster_user_code_image.name
  name    = "dagster_user_code"
  restart = "always"
  dns = [docker_container.dnsmasq_container.network_data[0].ip_address]

  env = [for k, v in local.env_dagster : "${k}=${v}"]

  volumes {
    host_path = abspath("${local.basepath}/dagster")
    container_path = "/opt/dagster/app"
  }

  volumes {
    host_path = abspath("${local.basepath}/_terraform/_data/dagster")
    container_path = "/opt/dagster/storage"
  }

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  volumes {
    host_path = abspath("${local.basepath}")
    container_path = "/east"
  }

  ports {
    internal = 4000
    external = 4000
  }

  networks_advanced {
    name = "${docker_network.east_network.name}"
    aliases = ["dagster_user_code"]
  }
}


resource "docker_container" "dagster_webserver" {
  image = docker_image.dagster_dagster_image.name
  name  = "dagster_webserver"
  dns = [docker_container.dnsmasq_container.network_data[0].ip_address]
  env   = [for k, v in local.env_dagster : "${k}=${v}"]

  volumes {
    host_path      = "/tmp/io_manager_storage"
    container_path = "/tmp/io_manager_storage"
  }

  volumes {
    host_path = abspath("${local.basepath}/dagster")
    container_path = "/opt/dagster/app"
  }

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  volumes {
    host_path = abspath("${local.basepath}")
    container_path = "/east"
  }

  volumes {
    host_path = abspath("${local.basepath}/_terraform/_data/dagster")
    container_path = "/opt/dagster/storage"
  }

  networks_advanced {
    name = "${docker_network.east_network.name}"
    aliases = ["dagster_webserver"]
  }

  depends_on = [
    docker_container.dagster_postgresql,
    docker_container.dagster_user_code
  ]

  ports {
    internal = 3000
    external = 3000
  }

  entrypoint = [
    "dagster-webserver",
    "-h",
    "0.0.0.0",
    "-p",
    "3000",
    "-w",
    "workspace.yaml"
  ]
}

resource "docker_container" "dagster_daemon" {
  image   = docker_image.dagster_dagster_image.name
  name    = "dagster_daemon"
  restart = "on-failure"
  dns = [docker_container.dnsmasq_container.network_data[0].ip_address]
  env     = [for k, v in local.env_dagster : "${k}=${v}"]

  volumes {
    host_path      = "/tmp/io_manager_storage"
    container_path = "/tmp/io_manager_storage"
  }

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  volumes {
    host_path = abspath("${local.basepath}/dagster")
    container_path = "/opt/dagster/app"
  }

  volumes {
    host_path = abspath("${local.basepath}/_terraform/_data/dagster")
    container_path = "/opt/dagster/storage"
  }

  volumes {
    host_path = abspath("${local.basepath}")
    container_path = "/east"
  }

  networks_advanced {
    name = "${docker_network.east_network.name}"
    aliases = ["dagster_daemon"]
  }

  depends_on = [
    docker_container.dagster_postgresql,
    docker_container.dagster_user_code
  ]

  entrypoint = [
    "dagster-daemon",
    "run"
  ]
}
