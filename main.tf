provider "azurerm" {
  features {}
}

resource "azurerm_container_group" "app_group" {
  name                = "myAppContainerGroup"
  location            = "East US"
  resource_group_name = "cloud-shell-storage-northeurope"

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

  image_registry_credential {
    server   = "questappacr.azurecr.io"
    username = "questappacr"        # Add ACR admin username or SP ID here
    password = "/srJbiW9+t+mTLh1rVtGWPJ/iXAilX7mCRMQMyKI8E+ACRDDUiTR"        # Add ACR admin password or SP password here
  }

  os_type = "Linux"
}
