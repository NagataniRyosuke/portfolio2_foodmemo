from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse


class mold(models.Model):
    Date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='pictures/',null=True,blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name if self.name else "Unnamed Memo"
    
    def get_absolute_url(self):
        return reverse('memo-detail',args=[str(self.id)])
    
    class Meta:
        ordering = ["completed"]
        
class ImageModel(models.Model):
    image = models.ImageField(upload_to='media/pictures/')
    is_rotated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_rotated:
            img_path = self.image.path
            with Image.open(img_path) as img: 
                rotated_img = img.rotate(90, expand=True)
                rotated_img.save(img_path)

    def __str__(self):
        return self.image.name
    
    def get_absolute_url(self):
        return reverse('detail-memo', args=[str(self.id)])  