import xml.etree.ElementTree as et

from uuid import uuid4

import untangle
import xmltodict

from django import forms

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

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


def detail(request, pk):
    recipe = get_recipe(pk)
    recipe = untangle.parse(recipe)

    ingredients_data = []
    for inglist in recipe.recipe.get_elements('ingredients'):
        for ing in inglist.get_elements('ingredient'):
            ingredients_data.append({
                'amount': ing.amount.value.cdata,
                'unit': ing.amount.unit.cdata,
                'name': ing.name.cdata
            })

    instructions_data = []
    for instlist in recipe.recipe.get_elements('instructions'):
        for inst in instlist.get_elements('ingredient'):
            instructions_data.append({
                'instruction': inst.text.cdata
            })

    ingredients = IngredientFormSet(prefix='ingredient', initial=ingredients_data)
    instructions = InstructionFormSet(prefix='instruction', initial=instructions_data)

    if request.method == 'POST':
        form = RecipeDetailForm(request.POST)

        cp = request.POST.copy()

        if 'add_ingredient' in request.POST:
            cp['ingredient-TOTAL_FORMS'] = int(cp['ingredient-TOTAL_FORMS']) + 1
        elif 'add_instruction' in request.POST:
            cp = request.POST.copy()
            cp['instruction-TOTAL_FORMS'] = int(cp['instruction-TOTAL_FORMS']) + 1
        elif 'save' in request.POST:
            ingredients = IngredientFormSet(request.POST, prefix='ingredient')
            instructions = InstructionFormSet(request.POST, prefix='instruction')

            if form.is_valid() and ingredients.is_valid():
                data = form.cleaned_data
                ingredient_data = ingredients.cleaned_data
                instruction_data = instructions.cleaned_data

                with recipe_db() as db:
                    db.replace(recipe_path(pk),
                        create_recipe_xml(pk, data['name'],
                                          ingredients=ingredient_data,
                                          instructions=instruction_data))

                return redirect('recipes.detail', pk=pk)

        instructions = InstructionFormSet(cp, prefix='instruction')
        ingredients = IngredientFormSet(cp, prefix='ingredient')
    else:
        form = RecipeDetailForm({
            'name': recipe.recipe.name.cdata
        })

    return render(request, 'recipes/detail.html',
                  {'form': form,
                   'ingredients': ingredients,
                   'ingredients_helper': IngredientInlineHelper(),
                   'instructions': instructions,
                   'instructions_helper': InstructionInlineHelper(),
                   'pk': pk})
