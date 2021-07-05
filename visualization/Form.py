from django import forms


class FileUploadForm(forms.Form):
    Select_File = forms.FileField()
