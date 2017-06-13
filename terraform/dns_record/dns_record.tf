variable "type" {}
variable "name" {}
variable "record" {}
variable "hostedzone_id" {}

resource "aws_route53_record" "dns-record" {
  name = "${var.name}"
  zone_id = "${var.hostedzone_id}"
  type = "${var.type}"
  ttl = "3600"
  records = ["${var.record}"]
}
