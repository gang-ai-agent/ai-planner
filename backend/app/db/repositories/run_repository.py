from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.run import AgentRun
from app.db.models.thread import Thread
from app.db.models.user import User


class RunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_thread_and_run(self, *, user_id: str, thread_id: str, run_id: str, status: str) -> None:
        user = await self.session.get(User, user_id)
        if user is None:
            self.session.add(User(id=user_id))

        thread = await self.session.get(Thread, thread_id)
        if thread is None:
            self.session.add(Thread(id=thread_id, user_id=user_id))

        run = await self.session.get(AgentRun, run_id)
        if run is None:
            self.session.add(AgentRun(id=run_id, thread_id=thread_id, status=status))
        else:
            run.status = status

        await self.session.flush()
