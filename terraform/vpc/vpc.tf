variable "vpc_name" {
  default = "Treadmill"
}

variable "vpc_cidr" {
  default = "172.23.0.0/16"
}

resource "aws_vpc" "vpc" {
  cidr_block = "${var.vpc_cidr}"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags {
    Name = "${var.vpc_name}"
  }
  lifecycle {
    create_before_destroy = true
  }
}

output "vpc_id"   { value = "${aws_vpc.vpc.id}" }
output "vpc_cidr" { value = "${aws_vpc.vpc.cidr_block}" }
