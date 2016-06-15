<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/amount/unit
    group by $name
    return <option>{ $name }</option>
}
</options>
