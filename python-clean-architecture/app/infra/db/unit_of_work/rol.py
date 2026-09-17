from app.infra.db import DBSession
from app.infra.db.repositories.rol import RolRepo
from app.infra.db.repositories.user import UserRepo
from app.infra.db.unit_of_work.base import BaseUnitOfWork


class RolUnitOfWork(BaseUnitOfWork):
    def __init__(self, session: DBSession) -> None:
        super().__init__(session)
        self.rol_repo = RolRepo(session)
        self.user_repo = UserRepo(session)


def rol_uow_factory(session: DBSession) -> RolUnitOfWork:
    return RolUnitOfWork(session)
