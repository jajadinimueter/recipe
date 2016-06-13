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
    current_date = datetime.datetime.now().isoformat('T')
    recipes = get_random_recipes(number_of_recipes=num_recipes,
                                 rating='good')

    eroot = et.Element('menuplans')
    emenuplan = et.SubElement(eroot, 'menuplan')
    emenuplan.append(et.fromstring(recipes))
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
