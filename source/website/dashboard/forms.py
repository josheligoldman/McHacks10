from django import forms


class AddClassForm(forms.Form):
    added_class = forms.CharField(label='Add Class', max_length=100)



