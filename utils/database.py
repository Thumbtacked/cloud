import bcrypt

class DatabaseWrapper:
    __slots__ = ("_pool", "_loop")

    def __init__(self, pool, loop):
        self._pool = pool
        self._loop = loop

    async def get_user_by_email(self, email):
        query = """
        SELECT *
        FROM users
        WHERE users.email = $1;
        """
        row = await self._pool.fetchrow(query, email)
        return User(row, self._pool, self._loop) if row else None

    async def get_user(self, user_id):
        query = """
        SELECT *
        FROM users
        WHERE users.id = $1;
        """
        row = await self._pool.fetchrow(query, user_id)
        return User(row, self._pool, self._loop) if row else None

    async def create_user(self, user_id, name, email, password, max_token_age):
        hashed_password = await self._loop.run_in_executor(
            None,
            bcrypt.hashpw,
            password.encode(),
            bcrypt.gensalt()
        )

        query = """
        INSERT INTO users (id, name, email, hashed_password, max_token_age)
        VALUES ($1, $2, $3, $4, $5);
        """
        await self._pool.execute(query, user_id, name, email, hashed_password.decode(), max_token_age)

class User:
    __slots__ = ("id", "name", "email", "_hashed_password", "max_token_age", "_pool", "_loop")

    def __init__(self, row, pool, loop):
        self.id = row["id"]
        self.name = row["name"]
        self.email = row["email"]
        self._hashed_password = row["hashed_password"]
        self.max_token_age = row["max_token_age"]
        self._pool = pool
        self._loop = loop

    async def update(self, *, name=None, email=None, password=None, max_token_age=None):
        self.name = name or self.name
        self.email = email or self.email
        self.max_token_age = max_token_age or self.max_token_age

        if password:
            self._hashed_password = (await self._loop.run_in_executor(
                None,
                bcrypt.hashpw,
                password.encode(),
                bcrypt.gensalt()
            )).decode()

        query = """
        UPDATE users
        SET name = $1, email = $2, hashed_password = $3, max_token_age = $4
        WHERE users.id = $5;
        """
        await self._pool.execute(query, self.name, self.email, self._hashed_password, self.max_token_age, self.id)

    async def check_password(self, password):
        password_matches = await self._loop.run_in_executor(
            None,
            bcrypt.checkpw,
            password.encode(),
            self._hashed_password.encode()
        )
        return password_matches
