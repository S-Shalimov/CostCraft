from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import ModelSelect2Widget
from .models import Types, Units, BasePrice, Estimate


class AddPrice(forms.ModelForm):
    types = forms.ModelChoiceField(queryset=Types.objects.all(), label=False,
                                   empty_label="Тип")
    units = forms.ModelChoiceField(queryset=Units.objects.all(), label=False,
                                   empty_label="Ед. изм.")
    price_dol = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    price_sum = forms.DecimalField(max_digits=20, decimal_places=2, required=False)

    price_dol.widget.attrs.update({'placeholder': 'Цена $'})
    price_sum.widget.attrs.update({'placeholder': 'Цена сум'})

    class Meta:
        model = BasePrice
        fields = ['name', 'units', 'price_dol', 'price_sum', 'types']

    def clean(self):
        cleaned_data = super().clean()
        price_dol = cleaned_data.get('price_dol')
        price_sum = cleaned_data.get('price_sum')
        if not price_dol and not price_sum:
            raise ValidationError('Заполните цену хотя бы в одной валюте')

class AddEstimate(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=BasePrice.objects.all(), label=False, empty_label="Наименование",
                                  widget=ModelSelect2Widget(model=Estimate,
                                                            search_fields=['name__icontains']))
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, label=False)
    units = forms.ModelChoiceField(queryset=Units.objects.all(), required=False, widget=forms.HiddenInput(attrs={'class': 'hidden'}))
    price_dol = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.HiddenInput(attrs={'class': 'hidden'}))
    types = forms.ModelChoiceField(queryset=Types.objects.all(), required=False, widget=forms.HiddenInput(attrs={'class': 'hidden'}))

    name.widget.attrs.update({'class': 'form-estimate__field-name', 'style': 'width:800px'})
    quantity.widget.attrs.update({'class': 'form-estimate__field-quantity', 'style': 'width:100px', 'placeholder': 'Кол-во'})

    class Meta:
        model = Estimate
        fields = ['name', 'quantity', 'units', 'price_dol', 'types']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            base_price = kwargs['instance'].name
            self.fields['units'].queryset = Units.objects.filter(pk=base_price.units.pk)
            self.fields['types'].queryset = Types.objects.filter(pk=base_price.types.pk)
#TODO: разобраться с тем, насколько нужно переопределение обоих методов
    def clean(self):
        cleaned_data = super().clean()

        quantity = cleaned_data.get('quantity')
        if quantity and quantity < 0:
            raise ValidationError('Количество не может быть отрицательным')

        base_price = cleaned_data.get('name')

        if base_price:
            cleaned_data['price_dol'] = base_price.price_dol
            units_qs = Units.objects.filter(units=base_price.units)
            if units_qs.exists():
                cleaned_data['units'] = units_qs.first()
            types_qs = Types.objects.filter(pk=base_price.types.pk)
            if types_qs.exists():
                cleaned_data['types'] = types_qs.first()
        return cleaned_data


class CollectEstimateUpload(forms.Form):
    dxf_scheme = forms.FileField(label='Загрузите dxf-чертёж',
                                 widget=forms.ClearableFileInput(attrs={'accept': '.dxf'})
                                 )


class ExchangeRateForm(forms.Form):
    rate = forms.DecimalField(label='Exchange rate', decimal_places=2, max_digits=10)