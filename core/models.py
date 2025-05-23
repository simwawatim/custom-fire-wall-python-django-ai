from django.db import models

class SSHConnection(models.Model):
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.source_ip} -> {self.destination_ip} ({self.status})"\


class BlockList(models.Model):
    url = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
