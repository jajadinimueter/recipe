from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import StrictButton

from django.core.urlresolvers import reverse


class MenuplanSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)

    helper = FormHelper()
    helper.form_class = 'form-inline'
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.layout = Layout(
        'query',
        Submit('search', 'Search', css_class='btn btn-default')
    )


class MenuplanCreateForm(forms.Form):
    menus = forms.IntegerField()
    people = forms.IntegerField()

    helper = FormHelper()
    helper.form_tag  = False
