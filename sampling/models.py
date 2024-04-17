from django.db import models

class Order(models.Model):
    orderno = models.IntegerField(primary_key = True)
    username = models.CharField(max_length = 250, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    sampletype = models.CharField(max_length=100)
    selected_samples = models.CharField(max_length = 800, null=True)
    completestatus = models.BooleanField(default = False)
    def __str__(self):
        return self.name

class register_user(models.Model):
    name = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 30)
    username = models.CharField(max_length = 100,primary_key = True)
    password = models.CharField(max_length = 128)
    def __str__(self):
        return self.username
    
class sampling_stock(models.Model):
    designid =  models.CharField(max_length = 100,primary_key = True, default = "Design_ID_Not_Provided")
    rackno = models.IntegerField()
    quantity = models.IntegerField()
    def __str__(self):
        return self.designid

class Designs(models.Model):
    image = models.ImageField(upload_to='designs/')
    name = models.CharField(max_length = 20,primary_key = True, default = 'No-Name')
    shade_color = models.CharField(max_length = 100, default = 'No-Shade')
    width = models.CharField(max_length = 50, default = 'No-Width')
    fabric_type = models.CharField(max_length = 50, default = 'No-Fabric Type')
    GSM = models.CharField(max_length = 50, default = 'No-GSM')
    pick = models.CharField(max_length = 50, default = 'No-Pick')
    weave = models.CharField(max_length = 50, default = 'No-Weave')
    finish = models.CharField(max_length = 80, default = 'No-Finish')
    description = models.TextField()
    def __str__(self):
        return self.name
    
class Bulk_Order(models.Model):
    image = models.ImageField(max_length = 150, default='/None/')
    orderno = models.IntegerField(primary_key = True)
    username = models.CharField(max_length = 250)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    selected_design = models.CharField(max_length = 80)
    length = models.CharField(max_length = 20)
    width = models.CharField(max_length = 20)
    completestatus = models.BooleanField(default = False)
    def __str__(self):
        return self.name