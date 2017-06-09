provider "aws" {
  region = "${var.region}"
}

module "vpc" {
  source = "vpc"
  vpc_cidr = "${var.vpc_cidr}"
  vpc_name = "${var.vpc_name}"
  subnet_name = "${var.subnet_name}"
  subnet_cidr = "${var.subnet_cidr}"
  az = "${lookup(var.az, var.region)}"
  region = "${var.region}"
  securtiygrp_name = "${var.securtiygrp_name}"
}

module "instance"  {
  source = "instance"
  role = "freeipa"
  ami_id = "${lookup(var.ami_id, var.region)}"
  key = "${var.key}"
  count = "1"
  size = "${lookup(var.size, var.role)}"
  subnet_id = "${module.vpc.subnet_id}"
  sg_id = "${module.vpc.sg_id}"
}