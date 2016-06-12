from django import forms

from crispy_forms.helper import FormHelper

from django.core.urlresolvers import reverse


class IngredientInlineForm(forms.Form):
    amount = forms.CharField(label='Amount')
    unit = forms.CharField(label='Unit')
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
