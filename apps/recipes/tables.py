from table import Table

from table.utils import A

from table.columns import Link
from table.columns import Column
from table.columns import LinkColumn


class RecipeTable(Table):
    name = Column(field='name', header='Name')
    links = LinkColumn(
        header='Actions',
        links=[
            Link(text='Edit', viewname='recipes.detail', args=(A('pk'), ))
        ]
    )
