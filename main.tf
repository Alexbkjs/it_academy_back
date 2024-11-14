provider "azurerm" {
  features {}
}

resource "azurerm_container_group" "app_group" {
  name                = "myAppContainerGroup"
  location            = "East US"
  resource_group_name = "myResourceGroup"

  container {
    name   = "fastapi"
    image  = "questappacr.azurecr.io/it_academy:latest"
    cpu    = "0.5"
    memory = "1.5"
    ports {
      port     = 9000
      protocol = "TCP"
    }
    environment_variables = {
      DATABASE_URL = "postgresql+asyncpg://admin:pass@db:5432/iar_db"
    }
  }

  container {
    name   = "postgres"
    image  = "postgres:latest"
    cpu    = "0.5"
    memory = "1.5"
    environment_variables = {
      POSTGRES_DB       = "iar_db"
      POSTGRES_USER     = "admin"
      POSTGRES_PASSWORD = "pass"
    }
  }

  os_type = "Linux"
}
