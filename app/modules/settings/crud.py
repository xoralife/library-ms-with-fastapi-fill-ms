from typing import Optional, Tuple
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.setting import Setting


class SettingCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Setting]:
        result = await self.db.execute(select(Setting).order_by(Setting.key))
        return list(result.scalars().all())

    async def get_by_key(self, key: str) -> Optional[Setting]:
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        return result.scalar_one_or_none()

    async def update_value(self, key: str, value: str) -> Optional[Setting]:
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            await self.db.flush()
        return setting

    async def get_setting_value(self, key: str, default: str = "") -> str:
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    async def seed_defaults(self) -> None:
        defaults = {
            "library_name": ("City Library", "Name of the library"),
            "borrow_days": ("14", "Default number of days for borrowing"),
            "fine_per_day": ("0.50", "Fine amount per overdue day in USD"),
            "max_borrow_limit": ("5", "Maximum books a student can borrow at once"),
            "max_renewals": ("2", "Maximum times a book can be renewed"),
            "reservation_expiry_days": ("3", "Days after which reservation expires"),
        }
        for key, (value, description) in defaults.items():
            existing = await self.get_by_key(key)
            if not existing:
                setting = Setting(key=key, value=value, description=description)
                self.db.add(setting)
        await self.db.flush()
