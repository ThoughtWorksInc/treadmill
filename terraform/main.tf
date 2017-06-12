provider "aws" {
  region = "${var.region}"
}

variable "name" {
  default = "Treadmill"
}
variable "vpc_cidr" {
  default = "172.23.0.0/16"
}

variable "region" {
  default = "us-east-1"
}

variable "domain" {
  default = "tw.treadmill."
}

module "vpc" {
  source = "vpc"
  vpc_name = "${var.name}-vpc"
  vpc_cidr = "${var.vpc_cidr}"
}

module "public_subnet" {
  source = "public_subnet"
  name   = "${var.name}-public"
  vpc_id = "${module.vpc.vpc_id}"
  region = "${var.region}"
}

module "security_group" {
  source = "security_group"
  secgroup_name = "${var.name}-secgroup"
  vpc_id = "${module.vpc.vpc_id}"
}

module "freeipa" {
  source = "instance"
  role = "freeipa"
  count = "1"
  subnet_id = "${module.public_subnet.subnet_id}"
  secgroup_id = "${module.security_group.secgroup_id}"
  region = "${var.region}"
  hostedzone_id = "${module.hostedzone.hostedzone_id}"
  domain = "${var.domain}"
}

module "treadmill-master" {
  source = "instance"
  role = "TreadmillMaster"
  count = "3"
  subnet_id = "${module.public_subnet.subnet_id}"
  secgroup_id = "${module.security_group.secgroup_id}"
  region = "${var.region}"
  hostedzone_id = "${module.hostedzone.hostedzone_id}"
  domain = "${var.domain}"
}

module "treadmill-node" {
  source = "instance"
  role = "TreadmillNode"
  count = "1"
  subnet_id = "${module.public_subnet.subnet_id}"
  secgroup_id = "${module.security_group.secgroup_id}"
  region = "${var.region}"
  hostedzone_id = "${module.hostedzone.hostedzone_id}"
  domain = "${var.domain}"
}

module "hostedzone" {
  source = "hostedzone"
  domain = "${var.domain}"
}
