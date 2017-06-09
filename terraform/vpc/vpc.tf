variable "region" {}

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

resource "aws_vpc" "vpc" {
  cidr_block = "${var.vpc_cidr}"
  tags {
    Name = "${var.vpc_name}"
  }
}

resource "aws_subnet" "subnet" {
  vpc_id = "${aws_vpc.vpc.id}"
  cidr_block = "${var.subnet_cidr}"
  availability_zone = "${lookup(var.az, var.region)}"
  tags {
    Name = "${var.subnet_name}"
  }
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = "${aws_vpc.vpc.id}"
}

resource "aws_route_table" "rtb" {
  vpc_id = "${aws_vpc.vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.gateway.id}"
  }
}

resource "aws_route_table_association" "association" {
  subnet_id = "${aws_subnet.subnet.id}"
  route_table_id = "${aws_route_table.rtb.id}"
}

resource "aws_security_group" "sg" {
  name = "${var.securtiygrp_name}"
  description = "allow inbound traffic from within vpc"
  vpc_id = "${aws_vpc.vpc.id}"

  tags {
    Name = "${var.securtiygrp_name}"
  }

  ingress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    self = true
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "vpc_id" {
  value = "${aws_vpc.vpc.id}"
}
output "subnet_id" {
  value = "${aws_subnet.subnet.id}"
}
output "secgroup_id" {
  value = "${aws_security_group.sg.id}"
}
