from django import forms

class skin_symptom_form(forms.Form):
    MY_CHOICES = [
        ('default', 'Select Symptom'),
        ('0', 'Itching'),
        ('1', 'Redness'),
        ('2', 'Rash'),
        ('3', 'Scaling'),
        ('4', 'Blister'),
        ('5', 'Pus Filled'),
        ('6', 'Pain'),
        ('7', 'Dry Skin'),
        ('8', 'Swelling'),
        ('9', 'Burning'),
        ('10', 'Cracks'),
        ('11', 'Circular Rash'),
        ('12', 'Oozing'),
        ('13', 'Fever'),
        ('14', 'Hair Loss'),
        ('15', 'Dark Spot'),
        ('16', 'Numbness'),
        ('17', 'Ulcer'),
        ('18', 'Peeling'),
        ('19', 'Thickness'),
    ]

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'type': 'text',
        'placeholder': 'Patient First Name'
    }), required=True)

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'type': 'text',
        'placeholder': 'Patient Last Name'
    }), required=True)

    contact = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': "form-control",
        'type': 'number',
        'placeholder': 'Patient Contact Number'
    }), required=True)

    age = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': "form-control",
        'type': 'number',
        'placeholder': 'Age'
    }), required=True)

    sym1 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES, required=True)
    sym2 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES, required=True)
    sym3 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES, required=True)
    sym4 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym5 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym6 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym7 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym8 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym9 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
    sym10 = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), choices=MY_CHOICES)
