from django import forms


def detect_card_type(number):
    number = number.replace(' ', '').replace('-', '')
    if number.startswith('9860'):
        return 'humo'
    if number.startswith('8600'):
        return 'uzcard'
    if number.startswith('4'):
        return 'visa'
    return 'other'


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100, label="To'liq ism",
        widget=forms.TextInput(attrs={'placeholder': "Ism Familiya", 'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20, label="Telefon raqam",
        widget=forms.TextInput(attrs={
            'placeholder': "+998 (90) 123-45-67",
            'class': 'form-control',
            'id': 'id_phone',
            'inputmode': 'tel',
            'autocomplete': 'tel',
        })
    )
    address = forms.CharField(
        label="Yetkazib berish manzili",
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': "Xaritadan joylashuv tanlaganda bu yerga avtomatik to'ldiriladi...",
            'id': 'id_address',
            'style': 'resize:none;background:#f8fafc;',
        })
    )
    payment_method = forms.ChoiceField(
        choices=[('cash', 'Naqd pul'), ('card', 'Karta orqali')],
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        label="To'lov usuli",
        initial='cash',
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2, 'class': 'form-control',
            'placeholder': "Qo'shimcha izoh (ixtiyoriy)..."
        }),
        required=False,
        label="Izoh",
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if digits.startswith('998'):
            digits = digits[3:]
        if len(digits) < 9:
            raise forms.ValidationError("Telefon raqamni to'g'ri kiriting (+998 XX XXX-XX-XX).")
        return phone


class CardPaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=19, label="Karta raqami",
        widget=forms.TextInput(attrs={
            'placeholder': "0000 0000 0000 0000",
            'class': 'form-control card-input',
            'autocomplete': 'cc-number',
            'inputmode': 'numeric',
            'id': 'id_card_number',
        })
    )
    expiry = forms.CharField(
        max_length=5, label="Muddati",
        widget=forms.TextInput(attrs={
            'placeholder': "MM/YY",
            'class': 'form-control',
            'autocomplete': 'cc-exp',
            'inputmode': 'numeric',
            'id': 'id_expiry',
        })
    )
    cvv = forms.CharField(
        max_length=4, label="CVV",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "•••",
            'class': 'form-control',
            'autocomplete': 'cc-csc',
            'inputmode': 'numeric',
            'type': 'password',
            'id': 'id_cvv',
        })
    )

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '').replace('-', '')
        if not number.isdigit() or len(number) != 16:
            raise forms.ValidationError("Karta raqamini to'g'ri kiriting (16 raqam).")
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data['expiry'].strip()
        if '/' not in expiry or len(expiry) != 5:
            raise forms.ValidationError("Format: MM/YY (masalan: 12/26).")
        month, year = expiry.split('/')
        if not month.isdigit() or not year.isdigit():
            raise forms.ValidationError("Noto'g'ri muddat.")
        if not (1 <= int(month) <= 12):
            raise forms.ValidationError("Oy 01 dan 12 gacha bo'lishi kerak.")
        return expiry

    def clean(self):
        cleaned = super().clean()
        number = cleaned.get('card_number', '')
        cvv = cleaned.get('cvv', '')
        if detect_card_type(number) == 'visa':
            if not cvv or not cvv.isdigit() or len(cvv) not in (3, 4):
                self.add_error('cvv', "VISA kartasi uchun CVV kiritish shart (3 yoki 4 raqam).")
        return cleaned
