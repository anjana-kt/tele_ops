from pydantic_settings import BaseSettings, SettingsConfigDict

'''
Magic: Pydantic BaseSettings
    Pydantic checks sources in a strict order of priority. When you call Settings(), it builds the final object using this hierarchy (from highest priority to lowest):
    - Explicit keyword arguments: If you passed something manually like Settings(postgres_port=5433), this wins over everything else.
    - Environment Variables: Actual environment variables set in your OS or Docker container (e.g., export POSTGRES_DB=foo).
    - The .env file: The file path you defined in your model_config.
    - Default values: The fallbacks defined directly in your class definition (e.g., postgres_host: str = "localhost").
    - It looks for environment variables or .env keys that match your field names case-insensitively or via standard normalization.
'''

class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Pydantic looks at model_config to extract key-value pairs
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        from sqlalchemy.engine import URL

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)

settings = Settings()