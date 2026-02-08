provider "aws" {
  region = "us-east-1"
}

# create a VPC
resource "aws_vpc" "vm_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "vm-vpc" }
}

# create an Internet Gateway
resource "aws_internet_gateway" "vm_igw" {
  vpc_id = aws_vpc.vm_vpc.id
}

# create a Route Table
resource "aws_route_table" "vm_route_table" {
  vpc_id = aws_vpc.vm_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vm_igw.id
  }
}

# create a Subnet
resource "aws_subnet" "vm_subnet" {
  vpc_id            = aws_vpc.vm_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true
}

# associate Route Table with Subnet
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.vm_subnet.id
  route_table_id = aws_route_table.vm_route_table.id
}

# create Security Group
resource "aws_security_group" "vm_sg" {
  name        = "vm_security_group"
  description = "Allow HTTP, SSH, and K8s NodePorts"
  vpc_id      = aws_vpc.vm_vpc.id

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_home_ip]
  }

  # Frontend Access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.my_home_ip]
  }

  # NodePort Range (Standard K8s NodePorts 30000-32767)
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = [var.my_home_ip]
  }

  # Outbound Traffic (Allow all)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}

# the Server (EC2 Instance)
resource "aws_instance" "k8s_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"

  subnet_id                   = aws_subnet.vm_subnet.id
  vpc_security_group_ids      = [aws_security_group.vm_sg.id]
  key_name                    = "bgvm-terraform"

  # below script runs once when the server starts
  user_data = <<-EOF
              #!/bin/bash
              # install K3s (Lightweight Kubernetes)
              curl -sfL https://get.k3s.io | sh -
              
              # allow the 'ubuntu' user to run kubectl
              mkdir -p /home/ubuntu/.kube
              cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
              chown ubuntu:ubuntu /home/ubuntu/.kube/config
              chmod 600 /home/ubuntu/.kube/config
              
              # add kubectl alias
              echo "alias k=kubectl" >> /home/ubuntu/.bashrc
              EOF

  tags = {
    Name = "VendingMachineCluster"
  }
}