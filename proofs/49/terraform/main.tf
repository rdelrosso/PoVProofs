#
# Configure the MongoDB Atlas Provider
#
terraform {
  required_providers {
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
      version = "0.8.2"
    }
  }
}


provider "mongodbatlas" {
  public_key  = var.public_key
  private_key = var.private_key
}

#
# Create a Shared Tier Cluster
#
resource "mongodbatlas_cluster" "RealmCluster" {
  project_id              = var.atlasprojectid
  name                    = "RealmCluster" 

  disk_size_gb            = "2"

  provider_name = "TENANT"
  backing_provider_name = "AWS"
  provider_region_name = "US_EAST_1"
  provider_instance_size_name = "M2"

  mongo_db_major_version = "4.4"
  auto_scaling_disk_gb_enabled = "false"
  }

resource "mongodbatlas_database_user" "realm-user" {
  username           = "realm-user"
  password           = "Passw0rd"
  project_id         = var.atlasprojectid
  auth_database_name = "admin"

  roles {
    role_name     = "readWrite"
    database_name = "sample_airbnb"
  }

}

# Use terraform output to display connection strings.
output "connection_string" {
value = replace(
  replace("${mongodbatlas_cluster.RealmCluster.connection_strings[0].standard}", "mongodb://", "mongodb://realm-user:Passw0rd@"),
  "/?ssl",
  "/sample_airbnb?ssl")
}
