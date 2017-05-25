resource "aws_instance" "saltmaster" {
	ami = "ami-f068a193"
	instance_type = "t2.micro"
	key_name = "ipa_singapore_key"
	subnet_id = "${aws_subnet.main.id}"
	vpc_security_group_ids = ["${aws_security_group.sg_common.id}"]
	associate_public_ip_address = true
	user_data = "${file("saltmaster.sh")}"

	tags {
		Name = "saltmaster"
	}
}
