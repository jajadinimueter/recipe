from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import StrictButton

from django.core.urlresolvers import reverse


class IngredientInlineForm(forms.Form):
    amount = forms.CharField(label='Amount')
    unit = forms.CharField(label='Unit', required=False)
    name = forms.CharField(label='Name')


IngredientFormSet = forms.formset_factory(IngredientInlineForm)


class InstructionInlineForm(forms.Form):
    instruction = forms.CharField(label='Instruction',
                                  widget=forms.Textarea())


InstructionFormSet = forms.formset_factory(InstructionInlineForm)


class IngredientInlineHelper(FormHelper):
    def __init__(self):
        super(IngredientInlineHelper, self).__init__()

        self.form_class = 'form-inline'
        self.template = 'bootstrap/table_inline_formset.html'
        self.form_tag  = False


class InstructionInlineHelper(FormHelper):
    def __init__(self):
        super(InstructionInlineHelper, self).__init__()

        self.form_class = 'form-inline'
        self.template = 'bootstrap/table_inline_formset.html'
        self.form_tag  = False


class RecipeCreateForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255)

    helper = FormHelper()
    helper.form_tag  = False


class RecipeDetailForm(RecipeCreateForm):
    helper = FormHelper()
    helper.form_tag  = False


class RecipeSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)

    helper = FormHelper()
    helper.form_class = 'form-inline'
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.layout = Layout(
        'query',
        Submit('search', 'Search', css_class='btn btn-default')
    )
