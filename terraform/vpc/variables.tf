variable "region"{
}
variable "vpc_name" {
  default = "Treadmill"
}
variable "vpc_cidr" {
  default = "172.23.0.0/16"
}
variable "subnet_name" {
  default = "Treadmill"
}
variable "subnet_cidr" {
  default = "172.23.1.0/24"
}
variable "securtiygrp_name" {
  default = "sg_common"
}

variable "az" {
  type = "map"
  default = {
    "us-east-1" = "us-east-1a"
    "us-east-2" = "us-east-2a"
    "ap-southeast-1" = "ap-southeast-1a"
    "ap-southeast-2" = "ap-southeast-2a"
    "us-west-1" = "us-west-1a"
    "us-west-2" = "us-west-2a"
  }
}
