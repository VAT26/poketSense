from django import forms

class SignupForm(forms.Form):
    username=forms.CharField(max_length=250,required=True)
    password=forms.CharField(widget=forms.PasswordInput,max_length=100,required=True,label="Password")
    confirm_password=forms.CharField(widget=forms.PasswordInput,max_length=100,required=True,label="Confirm Password")
    email=forms.EmailField(max_length=100,required=True,help_text="Enter a valid email address")

    def clean(self):
            cleaned_data = super().clean()
            password = cleaned_data.get("password")
            confirm_password = cleaned_data.get("confirm_password")

            if password and confirm_password and password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")

            return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True,label='username')
    password = forms.CharField(
        widget=forms.PasswordInput,
        max_length=100,
        required=True,
        label='password'
    )