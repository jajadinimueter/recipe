import xml.etree.ElementTree as et

from uuid import uuid4

import xmltodict

from django.shortcuts import render
from django.shortcuts import redirect

from .basex import recipe_db

from .forms import RecipeCreateForm
from .forms import RecipeDetailForm


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
import module namespace lib="custom/pagination";
let $result := lib:paged(collection("recipe")//recipe, 'recipes', 0, 50, true())
return $result
'''


def get_recipes():
    with recipe_db() as db:
        query = db.query(GET_RECIPES_QUERY)
        recipes = query.execute()

    return recipes


def get_recipe(pk):
    path = recipe_path(pk)

    with recipe_db() as db:
        query = db.query(GET_RECIPE_QUERY)
        query.bind('$path', path)
        recipe = query.execute()

    return recipe


def index(request):
    if request.method == 'GET':
        recipes = get_recipes()
        print(recipes)

    return render(request, 'recipes/index.html')


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
    recipe_dict = xmltodict.parse(recipe)

    if request.method == 'POST':
        form = RecipeDetailForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            recipe_dict['recipe']['name'] = data['name']

            doc = xmltodict.unparse(recipe_dict)

            with recipe_db() as db:
                db.replace(recipe_path(pk), doc)
    else:
        form = RecipeDetailForm({
            'name': recipe_dict['recipe']['name']
        })

    return render(request, 'recipes/detail.html', {'form': form, 'pk': pk})
