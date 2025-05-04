output "instance_ip" {
  value = aws_instance.k8s_master.public_ip
}