from __future__ import annotations

import argon2
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncpg
    import datetime
    from collections.abc import Mapping


class DatabaseWrapper:
    __slots__ = ("_pool", "_hasher")

    def __init__(self, pool: asyncpg.Pool):
        self._pool: asyncpg.Pool = pool
        self._hasher: argon2.PasswordHasher = argon2.PasswordHasher()

    async def get_user_by_email(self, email: str) -> User | None:
        query = """
        SELECT *
        FROM users
        WHERE users.email = $1;
        """

        row = await self._pool.fetchrow(query, email)
        return User(row, self) if row else None

    async def get_user(self, user_id: str) -> User | None:
        query = """
        SELECT *
        FROM users
        WHERE users.id = $1;
        """

        row = await self._pool.fetchrow(query, user_id)
        return User(row, self) if row else None

    async def create_user(
        self,
        user_id: str,
        name: str,
        email: str,
        password: str,
        max_token_age: datetime.datetime
    ) -> None:
        query = """
        INSERT INTO users (id, name, email, hashed_password, max_token_age)
        VALUES ($1, $2, $3, $4, $5);
        """

        hashed_password = await asyncio.to_thread(self._hasher.hash, password)
        await self._pool.execute(query, user_id, name, email, hashed_password, max_token_age)

class User:
    __slots__ = ("id", "name", "email", "_hashed_password", "max_token_age", "_database")

    def __init__(self, row: Mapping, database: DatabaseWrapper):
        self.id: str = row["id"]
        self.name: str = row["name"]
        self.email: str = row["email"]
        self._hashed_password: str = row["hashed_password"]
        self.max_token_age: datetime.datetime = row["max_token_age"]
        self._database = database

    async def update(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        max_token_age: datetime.datetime | None = None
    ):
        self.name = name or self.name
        self.email = email or self.email
        self.max_token_age = max_token_age or self.max_token_age

        if password:
            self._hashed_password = await asyncio.to_thread(self._database._hasher.hash, password)

        query = """
        UPDATE users
        SET name = $1, email = $2, hashed_password = $3, max_token_age = $4
        WHERE users.id = $5;
        """
        await self._database._pool.execute(query, self.name, self.email, self._hashed_password, self.max_token_age, self.id)

    async def check_password(self, password):
        password_matches = await asyncio.to_thread(self._database._hasher.verify, self._hashed_password, password)
        return password_matches
