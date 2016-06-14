import xml.etree.ElementTree as et

from uuid import uuid4

import untangle
import xmltodict

from django import forms

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from django.contrib import messages

from basex.basex import recipe_db

from .forms import RecipeCreateForm
from .forms import RecipeDetailForm
from .forms import RecipeSearchForm

from .forms import InstructionFormSet
from .forms import InstructionInlineHelper

from .forms import IngredientFormSet
from .forms import IngredientInlineHelper

from .tables import RecipeTable

from .dbaccess import *


def index(request):
    search_query = None

    if request.method == 'POST':
        search_form = RecipeSearchForm(request.POST)
    else:
        search_form = RecipeSearchForm()

    table_data = []

    recipes = get_recipes(search_form.data.get('query'))

    if recipes:
        document = untangle.parse(recipes)

        if int(document.recipes['total']) > 0:
            for recipe in document.recipes.recipe:
                pk = 0
                if hasattr(recipe, 'pk'):
                    pk = recipe.pk.cdata

                table_data.append({'name': recipe.name.cdata,
                                   'pk': pk})

    return render(request, 'recipes/index.html',
                  {'table': RecipeTable(table_data),
                   'search_form': search_form})


def create(request):
    if request.method == 'POST':
        form = RecipeCreateForm(request.POST)

        if form.is_valid():
            pk = add_recipe(form.cleaned_data)

            return redirect('recipes.detail', pk=pk)
    else:
        form = RecipeCreateForm()

    return render(request, 'recipes/create.html', {'form': form})


def get_options(doc):
    return [
        option.cdata
        for option in doc.options.get_elements()
    ]


def get_ingredient_options():
    return get_options(untangle.parse(get_ingredients()))


def get_unit_options():
    return get_options(untangle.parse(get_units()))


def get_comment_options():
    return get_options(untangle.parse(get_comments()))


def detail(request, pk):
    with recipe_db() as db:
        recipe = et.fromstring(get_recipe(pk))

        ingredient_options = get_ingredient_options()
        unit_options = get_unit_options()
        comment_options = get_comment_options()

        ingredients_data = []
        for ing in recipe.findall('.//ingredient'):
            ingredients_data.append({
                'amount': ing.findtext('amount/value'),
                'unit': ing.findtext('amount/unit'),
                'name': ing.findtext('name'),
                'comment': ing.findtext('comment'),
            })

        instructions_data = []
        for inst in recipe.findall('.//instruction'):
            instructions_data.append({
                'instruction': inst.findtext('text')
            })

        form_kwargs = {'db': db}

        ingredients = IngredientFormSet(prefix='ingredient', initial=ingredients_data,
                                        form_kwargs=form_kwargs)
        instructions = InstructionFormSet(prefix='instruction', initial=instructions_data,
                                          form_kwargs=form_kwargs)

        if request.method == 'POST':
            form = RecipeDetailForm(request.POST)

            cp = request.POST.copy()

            if 'add_ingredient' in request.POST:
                cp['ingredient-TOTAL_FORMS'] = int(cp['ingredient-TOTAL_FORMS']) + 1
            elif 'add_instruction' in request.POST:
                cp = request.POST.copy()
                cp['instruction-TOTAL_FORMS'] = int(cp['instruction-TOTAL_FORMS']) + 1
            elif 'save' in request.POST:
                ingredients = IngredientFormSet(request.POST, prefix='ingredient',
                                                form_kwargs=form_kwargs)
                instructions = InstructionFormSet(request.POST, prefix='instruction',
                                                  form_kwargs=form_kwargs)

                if form.is_valid() and ingredients.is_valid():
                    data = form.cleaned_data
                    ingredient_data = [f.cleaned_data for f in ingredients.forms
                                       if f not in ingredients.deleted_forms]
                    instruction_data = [f.cleaned_data for f in instructions.forms
                                       if f not in instructions.deleted_forms]

                    with recipe_db() as db:
                        db.replace(recipe_path(pk),
                            et.tostring(
                                create_recipe_xml(
                                    pk,
                                    data['name'],
                                    data['people'],
                                    data['rating'],
                                    ingredients=ingredient_data,
                                    instructions=instruction_data)))

                    messages.add_message(request, messages.SUCCESS, 'Recipe %s saved' % data['name'])

                    return redirect('recipes.detail', pk=pk)

            instructions = InstructionFormSet(cp, prefix='instruction',
                                              form_kwargs=form_kwargs)
            ingredients = IngredientFormSet(cp, prefix='ingredient',
                                            form_kwargs=form_kwargs)
        else:
            form = RecipeDetailForm({
                'name': recipe.findtext('name'),
                'people': recipe.findtext('people'),
                'rating': recipe.findtext('rating'),
            })

        return render(request, 'recipes/detail.html',
                      {'form': form,
                       'ingredients': ingredients,
                       'ingredients_helper': IngredientInlineHelper(),
                       'instructions': instructions,
                       'instructions_helper': InstructionInlineHelper(),
                       'pk': pk,
                       'ingredient_options': ingredient_options,
                       'unit_options': unit_options,
                       'comment_options': comment_options,
                       })
