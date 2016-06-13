import xml.etree.ElementTree as et

from dateutil import parser

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

import untangle

from .forms import MenuplanSearchForm
from .forms import MenuplanCreateForm

from .tables import MenuplanTable

from .dbaccess import add_menuplan
from .dbaccess import get_menuplans
from .dbaccess import create_menuplan


def index(request):
    search_query = None

    if request.method == 'POST':
        search_form = MenuplanSearchForm(request.POST)
    else:
        search_form = MenuplanSearchForm()

    table_data = []

    menuplans = get_menuplans(search_form.data.get('query'))

    if menuplans:
        document = untangle.parse(menuplans)

        if int(document.menuplans['total']) > 0:
            for menuplan in document.menuplans.get_elements():
                table_data.append({
                    'name': menuplan.name.cdata,
                    'creationDate': parser.parse(menuplan.creationDate.cdata),
                    'people': menuplan.people.cdata,
                    'pk': menuplan.pk.cdata
                })

    return render(request, 'menuplans/index.html',
                  {'table': MenuplanTable(table_data),
                   'search_form': search_form})


def create(request):
    if request.method == 'POST':
        form = MenuplanCreateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            pk, document = create_menuplan(data['people'], data['menus'])

            add_menuplan(pk, et.tostring(document))

            return redirect('menuplans.detail', pk=pk)
    else:
        form = MenuplanCreateForm()

    return render(request, 'menuplans/create.html', {'form': form})


def detail(request):
    pass
