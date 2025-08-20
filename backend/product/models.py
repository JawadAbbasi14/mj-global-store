from django.db import models
class Products(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    description = models.TextField(max_length=1000)



    class Meta:
        db_table = "product_table"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def __str__(self):
        return self.name
