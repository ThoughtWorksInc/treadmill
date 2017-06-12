variable "vpc_name" {}

variable "vpc_cidr" {}

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
