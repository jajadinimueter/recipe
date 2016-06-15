<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/name
    group by $name
    return <option>{ $name }</option>
}
</options>
