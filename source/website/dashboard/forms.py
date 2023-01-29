from django import forms


class AddClassForm(forms.Form):
    added_class = forms.CharField(
        label="",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Add Class',
                'class': 'add_class',
            }
        )
    )



