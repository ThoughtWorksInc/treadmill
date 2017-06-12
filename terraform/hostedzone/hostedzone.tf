variable "domain" {}
variable "vpc_id" {}

resource "aws_route53_zone" "hostedzone" {
  name = "${var.domain}"
  vpc_id = "${var.vpc_id}"
}

output "hostedzone_id" {
  value = "${aws_route53_zone.hostedzone.id}"
}