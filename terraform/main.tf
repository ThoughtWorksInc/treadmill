provider "aws" {
  region = "${var.region}"
}

module "vpc" {
  source = "vpc"
  region = "${var.region}"
}

module "freeipa" {
  source = "instance"
  role = "freeipa"
  count = "1"
  subnet_id = "${module.vpc.subnet_id}"
  secgroup_id = "${module.vpc.secgroup_id}"
  region = "${var.region}"
}

module "treadmill-master" {
  source = "instance"
  role = "TreadmillMaster"
  count = "3"
  subnet_id = "${module.vpc.subnet_id}"
  secgroup_id = "${module.vpc.secgroup_id}"
  region = "${var.region}"
}

module "treadmill-node" {
  source = "instance"
  role = "TreadmillNode"
  count = "1"
  subnet_id = "${module.vpc.subnet_id}"
  secgroup_id = "${module.vpc.secgroup_id}"
  region = "${var.region}"
}
