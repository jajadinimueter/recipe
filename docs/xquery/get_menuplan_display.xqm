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
