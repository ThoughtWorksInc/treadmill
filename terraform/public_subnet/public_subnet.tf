variable "region" {}
variable "vpc_id" {}

variable "subnet_name" {
  default = "Treadmill"
}

variable "subnet_cidr" {
  default = "172.23.1.0/24"
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

resource "aws_subnet" "subnet" {
  vpc_id = "${var.vpc_id}"
  cidr_block = "${var.subnet_cidr}"
  availability_zone = "${lookup(var.az, var.region)}"
  tags {
    Name = "${var.name}"
  }
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = "${var.vpc_id}"

  tags {
    Name = "${var.name}"
  }
}

resource "aws_route_table" "route_table" {
  vpc_id = "${var.vpc_id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.gateway.id}"
  }
}

resource "aws_route_table_association" "association" {
  subnet_id = "${aws_subnet.subnet.id}"
  route_table_id = "${aws_route_table.route_table.id}"
}


output "subnet_id" {
  value = "${aws_subnet.subnet.id}"
}
