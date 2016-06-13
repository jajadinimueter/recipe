from table import Table

from table.utils import A

from table.columns import Link
from table.columns import Column
from table.columns import LinkColumn


class MenuplanTable(Table):
    name = Column(field='name', header='Name')
    creationDate = Column(field='creationDate', header='Creation Date')
    links = LinkColumn(
        header='Actions',
        links=[
            Link(text='Open', viewname='menuplans.detail', args=(A('pk'), ))
        ]
    )
