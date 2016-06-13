from uuid import uuid4

import xml.etree.ElementTree as et

from basex.basex import recipe_db


__all__ = (
    'create_recipe',
    'recipe_path',
    'create_recipe_xml',
    'get_random_recipes',
    'get_recipes',
    'get_recipe',
    'add_recipe',
)


GET_RECIPE_QUERY = '''
declare variable $path external;

let $result := doc(concat('recipe/', $path))
return $result
'''

GET_RECIPES_QUERY = '''
import module namespace paging="custom/pagination";

declare variable $query as xs:string external;

let $selection :=
    for $recipe in collection("recipe")//recipe
    where $recipe[matches(upper-case(name), upper-case($query))] or
          $recipe//ingredient[matches(upper-case(name), upper-case($query))]
    return $recipe

let $result := paging:paged($selection, 'recipes', 0, 50, true())
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


def add_recipe(data):
    pk = str(uuid4())

    # Create a new document
    with recipe_db() as db:
        db.add(recipe_path(pk), create_recipe(pk, data))

    return pk


def create_recipe(pk, data):
    root = et.Element('recipe')
    ename = et.SubElement(root, 'name')
    ename.text = data['name']
    epk = et.SubElement(root, 'pk')
    epk.text = pk
    return et.tostring(root)


def recipe_path(pk):
    return 'recipes/%s.xml' % pk


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


def get_recipes(search_query):
    with recipe_db() as db:
        query = db.query(GET_RECIPES_QUERY)
        query.bind('$query', search_query or '')
        recipes = query.execute()

    return recipes.encode('utf8')


def get_recipe(pk):
    path = recipe_path(pk)

    with recipe_db() as db:
        query = db.query(GET_RECIPE_QUERY)
        query.bind('$path', path)
        recipe = query.execute()

    return recipe.encode('utf8')

