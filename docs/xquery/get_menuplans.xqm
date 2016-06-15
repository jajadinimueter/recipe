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
