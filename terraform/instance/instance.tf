resource "aws_instance" "freeipa" {
	ami = "${var.ami_id}"
	instance_type = "${var.size}"
	key_name = "${var.key}"
	subnet_id = "${var.subnet_id}"
	vpc_security_group_ids = ["var.sg_id"]
	associate_public_ip_address = true
	count = "${var.count}"
	tags {
		Name = "${var.role}"
		Id = "${count.index + 1}"
	}
}
