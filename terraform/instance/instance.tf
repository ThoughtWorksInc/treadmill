resource "aws_instance" "freeipa" {
	ami = "${lookup(var.ami_id, var.region)}"
	instance_type = "${lookup(var.size, var.role)}"
	key_name = "${var.key}"
	subnet_id = "${var.subnet_id}"
	vpc_security_group_ids = ["${var.sg_id}"]
	associate_public_ip_address = true
	count = "${var.count}"
	tags {
		Name = "${var.role}"
		Id = "${count.index + 1}"
	}
}
