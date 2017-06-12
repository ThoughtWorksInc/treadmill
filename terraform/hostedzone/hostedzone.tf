variable "domain" {}

resource "aws_route53_zone" "hostedzone" {
  name = "${var.domain}"
}

output "hostedzone_id" {
  value = "${aws_route53_zone.hostedzone.id}"
}