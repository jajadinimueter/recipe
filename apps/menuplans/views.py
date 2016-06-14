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
from .dbaccess import get_menuplan_display


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
                name = menuplan.name.cdata
                cd = parser.parse(menuplan.creationDate.cdata)
                cd = cd.strftime('%d.%m.%Y %H:%M')

                try:
                    nd = parser.parse(menuplan.name.cdata)
                    name = nd.strftime('%d.%m.%Y %H:%M')
                except:
                    pass

                table_data.append({
                    'name': name,
                    'creationDate': cd,
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


def join_non_empty(vals, sep=' '):
    return sep.join([x for x in vals if x and x.strip()])


def detail(request, pk):
    if request.method == 'GET':
        val = get_menuplan_display(pk)
        print(val)
        display = et.fromstring(val)

        menuplan = []
        shopping_list = []
        recipes = []

        for shopping_list_item in display.findall('.//shoppingListItem'):
            unit = shopping_list_item.findtext('unit', '')
            name = shopping_list_item.findtext('name')
            amount = float(shopping_list_item.findtext('amount'))

            if not amount:
                amount = ''

            alpha_values = shopping_list_item.findall('alphaAmounts/value')

            if amount or not alpha_values:
                shopping_list.append({
                    'name': name,
                    'amount': join_non_empty([str(amount), unit])
                })

            for alpha_value in alpha_values:
                shopping_list.append({
                    'name': name,
                    'amount': join_non_empty([alpha_value.text, unit])
                })

        for e_plan in display.findall('days//day'):
            menuplan.append({
                'day': e_plan.findtext('number'),
                'recipe': e_plan.findtext('recipe')
            })

        for e_recipe in display.findall('recipes//recipe'):
            e_ings = e_recipe.findall('.//ingredient')
            ingredients = []
            for e_ing in e_ings:
                ing_name = e_ing.findtext('name')
                ing_unit = e_ing.findtext('.//unit', '')
                ing_value = e_ing.findtext('.//value', '')
                ing_comment = e_ing.findtext('.//comment', '')

                ingredients.append(
                    join_non_empty([ing_value, ing_unit, ing_name, ing_comment]))

            ingredients = join_non_empty(ingredients, ', ')

            instructions = []
            einstructions = e_recipe.findall('.//instruction/text')
            for einst in einstructions:
                instructions.append(einst.text)

            recipes.append({
                'name': e_recipe.findtext('name'),
                'ingredients': ingredients,
                'instructions': instructions
            })

        print(recipes)

        return render(request,
                      'menuplans/detail.html',
                      {
                        'recipes': recipes,
                        'menuplan': menuplan,
                        'shopping_list': shopping_list,
                      })
