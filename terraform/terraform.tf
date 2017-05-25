terraform {
  backend "s3" {
    bucket = "treadmill-terraform-state-mumbai"
    key    = "terraform.tfstate"
    region = "ap-south-1"
  }
}