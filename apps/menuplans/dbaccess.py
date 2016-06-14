import datetime
from uuid import uuid4

import xml.etree.ElementTree as et

from basex.basex import recipe_db

from recipes.dbaccess import get_random_recipes


GET_MENUPLANS_QUERY = '''
import module namespace paging="custom/pagination";

declare variable $query as xs:string external;
declare variable $offset as xs:integer external;
declare variable $limit as xs:integer external;

let $upperQuery := upper-case($query)
let $selection :=
    for $menuplan in collection("recipe")//menuplan
    where $menuplan//recipe[matches(upper-case(name), $upperQuery)] or
          $menuplan//recipe//ingredient[matches(upper-case(name), $upperQuery)] or
          $menuplan[matches(upper-case(name), $upperQuery)]
    order by xs:dateTime($menuplan/creationDate) descending
    return $menuplan

let $result := paging:paged($selection, 'menuplans', $offset, $limit, true())
return $result
'''


GET_MENUPLAN_DISPLAY_QUERY = '''
declare variable $pk as xs:string external;

<menuplan>{
    let $doc := //menuplan[pk=$pk]
    return
        (<days>{
            for $recipe at $recipeIndex in $doc//recipe
            return <day>
                <number>{$recipeIndex}</number>
                <recipe>{$recipe/name/text()}</recipe>
            </day>
        }</days>,
        <recipes>{
            $doc//recipe
        }</recipes>,
        <shoppingList>{
        for $ingredient in distinct-values($doc//ingredient/name/text())
        order by $ingredient ascending
          return
              for $unit in distinct-values($doc//ingredient[name=$ingredient]/amount/unit)
                let $numericAmounts := $doc//ingredient[name=$ingredient]/amount[string(number(value)) != 'NaN' and unit=$unit]/value
                let $alphaAmounts := $doc//ingredient[name=$ingredient]/amount[string(number(value)) = 'NaN' and unit=$unit]/value/text()
                return <shoppingListItem>
                    <name>{$ingredient}</name>
                    <unit>{$unit}</unit>
                    <amount>{sum($numericAmounts)}</amount>
                    <alphaAmounts>{
                        for $a in $alphaAmounts
                            return <value>{$a}</value>
                    }</alphaAmounts>
                </shoppingListItem>
        }</shoppingList>)
}</menuplan>
'''

def get_menuplan_display(pk):
    with recipe_db() as db:
        q = db.query(GET_MENUPLAN_DISPLAY_QUERY)
        q.bind('$pk', pk)
        menuplans = q.execute()

        return menuplans.encode('utf8')


def get_menuplans(query=None, offset=0, limit=10):
    with recipe_db() as db:
        q = db.query(GET_MENUPLANS_QUERY)
        q.bind('$offset', str(offset))
        q.bind('$limit', str(limit))
        q.bind('$query', str(query or ''))
        menuplans = q.execute()

        return menuplans.encode('utf8')


def create_menuplan(people, num_recipes):
    pk = str(uuid4())
    people = int(people)
    current_date = datetime.datetime.now().isoformat('T')
    erecipes = et.fromstring(get_random_recipes(number_of_recipes=num_recipes,
                             rating='good'))

    for erecipe in erecipes:
        rpeople = erecipe.findtext('people')
        if rpeople:
            rpeople = float(rpeople)
            for evalue in erecipe.findall('.//amount/value'):
                if evalue.text and evalue.text.isdigit():
                    new_value = '%.2f' % (float(evalue.text) * float(people) / rpeople)
                    if new_value.endswith('.00'):
                        new_value = new_value.replace('.00', '')
                    evalue.text = new_value


    eroot = et.Element('menuplans')
    emenuplan = et.SubElement(eroot, 'menuplan')
    emenuplan.append(erecipes)
    ename = et.SubElement(emenuplan, 'name')
    ecreationDate = et.SubElement(emenuplan, 'creationDate')
    epeople = et.SubElement(emenuplan, 'people')
    epk = et.SubElement(emenuplan, 'pk')

    epk.text = pk
    ename.text = current_date
    ecreationDate.text = current_date
    epeople.text = str(people)

    return pk, eroot


def menuplan_path(pk):
    return 'menuplans/%s.xml' % pk


def add_menuplan(pk, menuplan):
    with recipe_db() as db:
        db.add(menuplan_path(pk), menuplan)
