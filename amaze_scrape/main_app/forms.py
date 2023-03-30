from django import forms
from .models.favorites import Wm_Product, Amazon_Product, Favorite

class ProductForm(forms.Form):
    wm_title = forms.CharField(max_length=255)
    wm_price = forms.DecimalField(max_digits=7, decimal_places=2)
    wm_link = forms.CharField(max_length=255)
    wm_imgLink = forms.CharField(max_length=255)
    amazon_title = forms.CharField(max_length=255)
    amazon_price = forms.DecimalField(max_digits=7, decimal_places=2)
    amazon_link = forms.CharField(max_length=255)
    amazon_imgLink = forms.CharField(max_length=255)
    grade = forms.IntegerField()

    # def save(self):
    #     wm_product = Wm_Product.objects.create(
    #         wm_title=self.cleaned_data['wm_title'],
    #         wm_price=self.cleaned_data['wm_price'],
    #         wm_link=self.cleaned_data['wm_link'],
    #         wm_imgLink=self.cleaned_data['wm_imgLink'],
    #         grade=self.cleaned_data['grade']
    #     )
    #     amazon_product = Amazon_Product.objects.create(
    #         amazon_title=self.cleaned_data['amazon_title'],
    #         amazon_price=self.cleaned_data['amazon_price'],
    #         amazon_link=self.cleaned_data['amazon_link'],
    #         amazon_imgLink=self.cleaned_data['amazon_imgLink']
    #     )
    #     product = Favorite.objects.create(
    #         wm_product=wm_product,
    #         amazon_product=amazon_product,
    #         user = self.user,
    #         # grade=self.cleaned_data['grade']
    #     )
    #     return product