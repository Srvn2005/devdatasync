resource "aws_instance" "k8s_master" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = var.instance_type
  key_name      = var.key_name

  tags = {
    Name = "k8s-master"
  }

  provisioner "local-exec" {
    command = "echo '${self.public_ip}' > ../ansible/hosts_ip.txt"
  }
}