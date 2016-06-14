from uuid import uuid4

import xml.etree.ElementTree as et

from basex.basex import recipe_db


__all__ = (
    'recipe_path',
    'create_recipe_xml',
    'get_random_recipes',
    'get_recipes',
    'get_recipe',
    'add_recipe',
    'get_ingredients',
    'get_units',
    'get_comments',
)


GET_RECIPE_QUERY = '''
declare variable $path external;

let $result := doc(concat('recipe/', $path))/recipes/recipe
return $result
'''

GET_RECIPES_QUERY = '''
import module namespace paging="custom/pagination";

declare variable $query as xs:string external;

let $selection :=
    for $recipe in collection("recipe")/recipes/recipe
    where $recipe[matches(upper-case(name), upper-case($query))] or
          $recipe//ingredient[matches(upper-case(name), upper-case($query))]
    return $recipe

let $result := paging:paged($selection, 'recipes', 0, 500, true())
return $result
'''


GET_RANDOM_RECIPES_QUERY = '''
import module namespace rand="http://basex.org/modules/random";
import module namespace paging="custom/pagination";

declare variable $num as xs:integer external;
declare variable $rating as xs:string external;

let $recipes :=
  for $recipe in collection("recipe")/recipes/recipe
  (: where $recipe[matches(upper-case(rating), upper-case($rating))]:)
  order by rand:integer()
  return $recipe

let $result := paging:paged($recipes, 'recipes', 1, $num, true())
return $result'''


GET_INGREDIENTS_QUERY = '''
<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/name
    group by $name
    return <option>{ $name }</option>
}
</options>
'''

GET_UNITS_QUERY = '''
<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/amount/unit
    group by $name
    return <option>{ $name }</option>
}
</options>
'''

GET_COMMENTS_QUERY = '''
<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/comment
    group by $name
    return <option>{ $name }</option>
}
</options>
'''


def get_ingredients():
    with recipe_db() as db:
        query = db.query(GET_INGREDIENTS_QUERY)
        return query.execute().encode('utf8')


def get_units():
    with recipe_db() as db:
        query = db.query(GET_UNITS_QUERY)
        return query.execute().encode('utf8')


def get_comments():
    with recipe_db() as db:
        query = db.query(GET_COMMENTS_QUERY)
        return query.execute().encode('utf8')


def add_recipe(data):
    pk = str(uuid4())

    recipe_xml = create_recipe_xml(pk, data['name'], data['people'], data['rating'])

    # Create a new document
    with recipe_db() as db:
        db.add(recipe_path(pk), et.tostring(recipe_xml))

    return pk


def recipe_path(pk):
    return 'recipes/%s.xml' % pk


def create_recipe_xml(pk, name, people, rating, ingredients=None, instructions=None):
    ingredients = ingredients or []
    instructions = instructions or []

    recipes = et.Element('recipes')
    erecipe = et.SubElement(recipes, 'recipe')
    ename = et.SubElement(erecipe, 'name')
    epeople = et.SubElement(erecipe, 'people')
    erating = et.SubElement(erecipe, 'rating')
    ename.text = name
    epeople.text = str(people)
    erating.text = rating
    epk = et.SubElement(erecipe, 'pk')
    epk.text = pk
    einsts = et.SubElement(erecipe, 'instructions')
    eings = et.SubElement(erecipe, 'ingredients')

    for ingredient in ingredients:
        if ingredient:
            eing = et.SubElement(eings, 'ingredient')
            eingname = et.SubElement(eing, 'name')
            eingcomment = et.SubElement(eing, 'comment')
            eingamount = et.SubElement(eing, 'amount')
            eingunit = et.SubElement(eingamount, 'unit')
            eingvalue = et.SubElement(eingamount, 'value')

            eingname.text = ingredient['name']
            eingunit.text = ingredient['unit']
            eingvalue.text = ingredient['amount']
            eingcomment.text = ingredient['comment']

    for instruction in instructions:
        if instruction:
            einst = et.SubElement(einsts, 'instruction')
            einsttext = et.SubElement(einst, 'text')

            einsttext.text = instruction['instruction']

    return recipes


def get_random_recipes(number_of_recipes=7, rating=None):
    with recipe_db() as db:
        query = db.query(GET_RANDOM_RECIPES_QUERY)
        query.bind('$num', str(number_of_recipes))
        query.bind('$rating', str(rating or ''))
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

