import module namespace paging="custom/pagination";

declare variable $query as xs:string external;

let $selection :=
    for $recipe in collection("recipe")/recipes/recipe
    where $recipe[matches(upper-case(name), upper-case($query))] or
          $recipe//ingredient[matches(upper-case(name), upper-case($query))]
    return $recipe

let $result := paging:paged($selection, 'recipes', 0, 500, true())
return $result
