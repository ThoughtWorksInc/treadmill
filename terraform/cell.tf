resource "aws_security_group" "sg_common" {
	name = "sg_common"
	description = "allow inbound traffic from within vpc"
	vpc_id = "${aws_vpc.main.id}"
	
	tags {
		Name = "sg_common"
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

data "template_file" "user_data" {
	template = "${file("salt-minion.tpl")}"
	vars {
		master_ip = "${aws_instance.saltmaster.private_ip}" 
	}
}

resource "aws_instance" "master" {
	ami = "ami-f068a193"
	instance_type = "t2.micro"
	key_name = "ipa_singapore_key"
	subnet_id = "${aws_subnet.main.id}"
	vpc_security_group_ids = ["${aws_security_group.sg_common.id}"]
	associate_public_ip_address = true
	user_data = "${data.template_file.user_data.rendered}" 
	tags {
		Name = "treadmillmaster"
		Id = "1"
	}
}

