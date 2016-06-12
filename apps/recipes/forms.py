from django import forms


class RecipeCreateForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255)


class RecipeDetailForm(RecipeCreateForm):
    pass
