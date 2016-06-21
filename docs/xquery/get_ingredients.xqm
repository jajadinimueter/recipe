declare variable $path external;

let $result := doc(concat('recipe/', $path))/recipes/recipe
return $result
