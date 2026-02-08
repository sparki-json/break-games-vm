variable "my_home_ip" {
  description = "My personal IP address for SSH access"
  type        = string
  sensitive   = true  # prevents Terraform from showing it in CLI output
}