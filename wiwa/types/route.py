from typing import NotRequired, TypedDict


RouteParams = dict[str, str]


class Route(TypedDict):
    handler: str
    params: RouteParams
    method: str
    auth_required: bool
    roles: list[str]
    template: NotRequired[str]
