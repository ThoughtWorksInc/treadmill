provider "aws" {
  region = "${var.region}"
}

module "vpc" {
  source = "vpc"
  region = "${var.region}"
}

module "instance"  {
  source = "instance"
  role = "freeipa"
  count = "1"
  subnet_id = "${module.vpc.subnet_id}"
  sg_id = "${module.vpc.sg_id}"
  region = "${var.region}"
}