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
return $result
