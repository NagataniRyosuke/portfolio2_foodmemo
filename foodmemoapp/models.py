from django.db import models
from django.contrib.auth.models import User

class mold(models.Model):
    Date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='pictures/',null=True,blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["completed"]
