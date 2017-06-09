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

resource "aws_internet_gateway" "gw" {
	vpc_id = "${aws_vpc.vpc.id}"
}

resource "aws_route_table" "rtb" {
	vpc_id = "${aws_vpc.vpc.id}"
	route {
		cidr_block = "0.0.0.0/0"
		gateway_id = "${aws_internet_gateway.gw.id}"
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