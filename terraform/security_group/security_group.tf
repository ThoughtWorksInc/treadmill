var "secgroup_name" {}
var "vpc_id" {}

resource "aws_security_group" "secgroup" {
  name = "${var.secgroup_name}"
  description = "allow inbound traffic from within vpc"
  vpc_id = "${var.vpc_id}"

  tags {
    Name = "${var.secgroup_name}"
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

output "secgroup_id" {
  value = "${aws_security_group.secgroup.id}"
}
