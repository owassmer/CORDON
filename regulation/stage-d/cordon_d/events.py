"""Select administrative anchors without upgrading dates or changing recipients."""
from dataclasses import dataclass
from datetime import date, datetime

from cordon_c.core import MissingInput
from .evidence import Support, instant


@dataclass(frozen=True)
class AdministrativeEvent:
    identity: str
    kind: str
    document: str
    recipient: str | None
    occurred: date | datetime
    support: Support

    def __post_init__(self):
        if not self.identity or not self.kind or not self.document or not isinstance(self.support, Support):
            raise ValueError('An event needs its source occurrence, kind, document and support')
        if isinstance(self.occurred, datetime):
            instant(self.occurred)
        elif type(self.occurred) is not date:
            raise TypeError('Preserve the source event precision')

    def anchor(self, *, kind: str, document: str, recipient: str | None,
               precision: str) -> date | datetime:
        if (kind, document, recipient) != (self.kind, self.document, self.recipient):
            raise ValueError('Wrong event kind, document or recipient for this anchor')
        if precision == 'date':
            return self.occurred.date() if isinstance(self.occurred, datetime) else self.occurred
        if precision == 'instant':
            if not isinstance(self.occurred, datetime):
                raise MissingInput('Actual event instant; a published date cannot supply elapsed hours')
            return self.occurred
        raise ValueError('Anchor precision must be date or instant')
