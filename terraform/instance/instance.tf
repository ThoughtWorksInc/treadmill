variable "region" {}

variable "key" {}

variable "count" {}

variable "subnet_id" {}

variable "secgroup_id" {}

variable "role" {}

variable "tm_repo" {}

variable "git_branch" {}

variable "hostedzone_id" {}

variable "ami_id" {
  type = "map"
  default = {
    "us-east-1" = "ami-6d1c2007"
    "us-east-2" = "ami-6a2d760f"
    "ap-southeast-1" = "ami-f068a193"
    "ap-southeast-2" = "ami-fedafc9d"
    "us-west-1" = "ami-af4333cf"
    "us-west-2" = "ami-d2c924b2"
  }
}

variable "size" {
  type = "map"
  default = {
    "freeipa" = "t2.small"
    "TreadmillMaster" = "t2.small"
    "TreadmillNode" = "t2.xlarge"
  }
}

data "template_file" "user_data" {
  template = "${file("user_data.tpl")}"
  vars {
    role = "${var.role}"
    tm_repo = "${var.tm_repo}"
    git_branch = "${var.git_branch}"
  }
}

resource "aws_instance" "instance" {
  ami = "${lookup(var.ami_id, var.region)}"
  instance_type = "${lookup(var.size, var.role)}"
  key_name = "${var.key}"
  subnet_id = "${var.subnet_id}"
  vpc_security_group_ids = ["${var.secgroup_id}"]
  associate_public_ip_address = true
  count = "${var.count}"
  user_data = "${data.template_file.user_data.rendered}"
  tags {
    Name = "${var.role}"
    Id = "${count.index + 1}"
  }
}

resource "aws_route53_record" "dns-entry" {
  count = "${var.count}"
  name = "${element(aws_instance.instance.*.tags.Name, count.index)}${element(aws_instance.instance.*.tags.Id, count.index)}"
  zone_id = "${var.hostedzone_id}"
  type = "A"
  ttl = "3600"
  records = ["${element(aws_instance.instance.*.private_ip, count.index)}"]
}
