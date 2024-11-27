terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  location = "North Europe"
}

resource "azurerm_resource_group" "it_academy_aci_caddy" {
  name     = "it-academy-aci-caddy"
  location = local.location
}

resource "azurerm_storage_account" "it_academy_aci_caddy" {
  name                      = "itacademyacicaddy"
  resource_group_name       = azurerm_resource_group.it_academy_aci_caddy.name
  location                  = azurerm_resource_group.it_academy_aci_caddy.location
  account_tier              = "Standard"
  account_replication_type  = "LRS"
  enable_https_traffic_only = true
}

resource "azurerm_storage_share" "it_academy_aci_caddy" {
  name               = "it-academy-aci-caddy-data"
  storage_account_name = azurerm_storage_account.it_academy_aci_caddy.name
  quota                = 1
}

resource "azurerm_container_group" "it_academy_aci_caddy" {
  resource_group_name = azurerm_resource_group.it_academy_aci_caddy.name
  location            = local.location
  name                = "it-academy-aci-caddy"
  os_type             = "Linux"
  dns_name_label      = "it-academy-aci-caddy"
  ip_address_type     = "public"


  image_registry_credential {
  server   = "questappacr.azurecr.io" # ACR server URL
  username = "questappacr"    # ACR username
  password = "/srJbiW9+t+mTLh1rVtGWPJ/iXAilX7mCRMQMyKI8E+ACRDDUiTR"    # ACR password
    }

  container {
    name   = "app"
    image  = "questappacr.azurecr.io/fastapi:latest"
    cpu    = "0.5"
    memory = "0.5"

    ports {
      port     = 9000                             # Port as specified in the YAML
      protocol = "TCP"
    }

    environment_variables = {
      DATABASE_URL = "postgresql+asyncpg://admin:pass@it-academy-rpg-db.northeurope.azurecontainer.io:5432/iar_db"  # Database URL
      BOT_TOKEN    = "7201821525:AAH7loon08xcZTodc9tVUc1zH4zaZXd3fZA"             # Bot token
    }
  }

  container {
    name   = "caddy"
    image  = "questappacr.azurecr.io/caddy:latest"
    cpu    = "0.5"
    memory = "0.5"

    ports {
      port     = 443
      protocol = "TCP"
    }

    ports {
      port     = 80
      protocol = "TCP"
    }

    volume {
      name                 = "it-academy-aci-caddy-data"
      mount_path           = "/data"
      storage_account_name = azurerm_storage_account.it_academy_aci_caddy.name
      storage_account_key  = azurerm_storage_account.it_academy_aci_caddy.primary_access_key
      share_name           = azurerm_storage_share.it_academy_aci_caddy.name
    }

    commands = ["caddy", "reverse-proxy", "--from", "it-academy-aci-caddy.northeurope.azurecontainer.io", "--to", "localhost:9000"]
  }
}

output "url" {
  value       = azurerm_container_group.it_academy_aci_caddy.fqdn
  description = "URL"
}
