<options>
{
    for $name in collection('recipe')/recipes/recipe//ingredient/comment
    group by $name
    return <option>{ $name }</option>
}
</options>
