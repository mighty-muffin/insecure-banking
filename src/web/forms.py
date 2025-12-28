"""Forms for the web application."""

from django import forms

from web.models import Transfer


class LoginForm(forms.Form):
    """Form for user login."""

    username = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    password = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )

    def clean_username(self):
        """Clean and validate username field."""
        username = self.cleaned_data.get("username")
        if not username:
            raise forms.ValidationError("Username is required")
        return username

    def clean_password(self):
        """Clean and validate password field."""
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError("Password is required")
        return password


class TransferForm(forms.ModelForm):
    """Form for creating transfers."""

    class Meta:
        model = Transfer
        fields = ["fromAccount", "toAccount", "description", "amount", "fee"]
        widgets = {
            "fromAccount": forms.Select(attrs={"class": "form-control"}),
            "toAccount": forms.TextInput(attrs={"class": "form-control", "placeholder": "Recipient Account"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Description"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount"}),
            "fee": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Fee"}),
        }

    def clean_amount(self):
        """Validate transfer amount."""
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

    def clean(self):
        """Validate entire form."""
        cleaned_data = super().clean()
        from_account = cleaned_data.get("fromAccount")
        to_account = cleaned_data.get("toAccount")

        # Note: Intentionally allowing same account transfers for educational purposes
        # In production, you would add validation here

        return cleaned_data


class AvatarUploadForm(forms.Form):
    """Form for uploading avatar images."""

    imageFile = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def clean_imageFile(self):
        """Validate uploaded image."""
        image = self.cleaned_data.get("imageFile")
        if image:
            # Validate file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 5MB")
        return image
