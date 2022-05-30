
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
resource "mongodbatlas_cluster" "pov-terraform" {
  project_id              = var.atlasprojectid
  name                    = "pov-terraform" 
  num_shards                   = 1
  replication_factor           = 3
  provider_backup_enabled      = true
  auto_scaling_disk_gb_enabled = var.auto_scaling_disk_gb_enabled
  mongo_db_major_version       = var.mongo_db_major_version

  //Provider settings
  provider_name               = var.atlas_provider_name
  provider_instance_size_name = var.atlas_provider_instance_size_name
  provider_region_name        = var.cluster_region
  }



# Use terraform output to display connection strings.
output "connection_strings" {
value = ["${mongodbatlas_cluster.pov-terraform.connection_strings}"]
}
