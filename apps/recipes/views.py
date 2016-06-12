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

from .forms import InstructionFormSet
from .forms import InstructionInlineHelper

from .forms import IngredientFormSet
from .forms import IngredientInlineHelper

from .tables import RecipeTable


def index(request):
    if request.method == 'GET':
        pass


def create_recipe(pk, data):
    root = et.Element('recipe')
    ename = et.SubElement(root, 'name')
    ename.text = data['name']
    epk = et.SubElement(root, 'pk')
    epk.text = pk
    return et.tostring(root)


def recipe_path(pk):
    return 'recipes/%s.xml' % pk


GET_RECIPE_QUERY = '''
declare variable $path external;

let $result := doc(concat('recipe/', $path))
return $result
'''

GET_RECIPES_QUERY = '''
import module namespace paging="custom/pagination";

let $result := paging:paged(collection("recipe")//recipe, 'recipes', 0, 50, true())
return $result
'''


GET_RANDOM_RECIPES_QUERY = '''
import module namespace rand="http://basex.org/modules/random";
import module namespace paging="custom/pagination";

declare variable $num as xs:integer external;

let $recipes :=
  for $recipe in collection("recipe")//recipe
  order by rand:integer()
  return $recipe

let $result := paging:paged($recipes, 'recipes', 1, $num, true())
return $result'''


def create_recipe_xml(pk, name, ingredients=None, instructions=None):
    ingredients = ingredients or []
    instructions = instructions or []

    root = et.Element('recipe')
    ename = et.SubElement(root, 'name')
    ename.text = name
    epk = et.SubElement(root, 'pk')
    epk.text = pk
    einsts = et.SubElement(root, 'instructions')
    eings = et.SubElement(root, 'ingredients')

    for ingredient in ingredients:
        if ingredient:
            eing = et.SubElement(eings, 'ingredient')
            eingname = et.SubElement(eing, 'name')
            eingamount = et.SubElement(eing, 'amount')
            eingunit = et.SubElement(eingamount, 'unit')
            eingvalue = et.SubElement(eingamount, 'value')

            eingname.text = ingredient['name']
            eingunit.text = ingredient['unit']
            eingvalue.text = ingredient['amount']

    for instruction in instructions:
        if instruction:
            einst = et.SubElement(einsts, 'instruction')
            einsttext = et.SubElement(einst, 'text')

            einsttext.text = instruction['instruction']

    return et.tostring(root)


def get_random_recipes(number_of_recipes=7):
    with recipe_db() as db:
        query = db.query(GET_RANDOM_RECIPES_QUERY)
        query.bind('$num', str(number_of_recipes))
        recipes = query.execute()

    return recipes.encode('utf-8')


def get_recipes():
    with recipe_db() as db:
        query = db.query(GET_RECIPES_QUERY)
        recipes = query.execute()

    return recipes.encode('utf8')


def get_recipe(pk):
    path = recipe_path(pk)

    with recipe_db() as db:
        query = db.query(GET_RECIPE_QUERY)
        query.bind('$path', path)
        recipe = query.execute()

    return recipe.encode('utf8')


def index(request):
    if request.method == 'GET':
        table_data = []

        # recipes = get_recipes()
        recipes = get_random_recipes(4)

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
                      {'table': RecipeTable(table_data)})


def create(request):
    if request.method == 'POST':
        form = RecipeCreateForm(request.POST)

        if form.is_valid():
            pk = str(uuid4())

            # Create a new document
            with recipe_db() as db:
                db.add(recipe_path(pk), create_recipe(pk, form.cleaned_data))

            return redirect('recipes.detail', pk=pk)
    else:
        form = RecipeCreateForm()

    return render(request, 'recipes/create.html', {'form': form})


def detail(request, pk):
    recipe = get_recipe(pk)
    recipe = untangle.parse(recipe)

    ingredients_data = [
        {
            'amount': ing.amount.value.cdata,
            'unit': ing.amount.unit.cdata,
            'name': ing.name.cdata
        }
        for ing in recipe.recipe.ingredients.ingredient
    ]

    instructions_data = []
    for instlist in recipe.recipe.instructions:
        for inst in instlist.get_elements():
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
