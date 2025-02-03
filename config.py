import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'S0methingVerySecur@')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///keys.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SNOWFLAKE_API_URL = None
    SNOWFLAKE_AUTH_TOKEN = None
    SNOWFLAKE_LLM_MODELS = { "snowflake[claude-3-5-sonnet]": {"model": "claude-3-5-sonnet", "max_tokens": 18000},
        "snowflake[deepseek-r1]": {"model": "deepseek-r1", "max_tokens": 128000},
        "snowflake[gemma-7b]": {"model": "gemma-7b", "max_tokens": 8000},
        "snowflake[jamba-1.5-large]": {"model": "jamba-1.5-large", "max_tokens": 256000},
        "snowflake[jamba-1.5-mini]": {"model": "jamba-1.5-mini", "max_tokens": 256000},
        "snowflake[jamba-instruct]": {"model": "jamba-instruct", "max_tokens": 256000},
        "snowflake[llama2-70b-chat]": {"model": "llama2-70b-chat", "max_tokens": 4096},
        "snowflake[llama3-70b]": {"model": "llama3-70b", "max_tokens": 4096},
        "snowflake[llama3-8b]": {"model": "llama3-8b", "max_tokens": 4096},
        "snowflake[llama3.1-405b]": {"model": "llama3.1-405b", "max_tokens": 128000},
        "snowflake[llama3.1-70b]": {"model": "llama3.1-70b", "max_tokens": 128000},
        "snowflake[llama3.1-8b]": {"model": "llama3.1-8b", "max_tokens": 128000},
        "snowflake[llama3.2-1b]": {"model": "llama3.2-1b", "max_tokens": 128000},
        "snowflake[llama3.2-3b]": {"model": "llama3.2-3b", "max_tokens": 128000},
        "snowflake[llama3.3-70b]": {"model": "llama3.3-70b", "max_tokens": 4096},
        "snowflake[mistral-7b]": {"model": "mistral-7b", "max_tokens": 32000},
        "snowflake[mistral-large]": {"model": "mistral-large", "max_tokens": 32000},
        "snowflake[mistral-large2]": {"model": "mistral-large2", "max_tokens": 128000},
        "snowflake[mixtral-8x7b]": {"model": "mixtral-8x7b", "max_tokens": 32000},
        "snowflake[reka-core]": {"model": "reka-core", "max_tokens": 32000},
        "snowflake[reka-flash]": {"model": "reka-flash", "max_tokens": 100000},
        "snowflake[snowflake-arctic]": {"model": "snowflake-arctic", "max_tokens": 4096},
        "snowflake[snowflake-llama-3.1-405b]": {"model": "snowflake-llama-3.1-405b", "max_tokens": 128000},
        "snowflake[snowflake-llama-3.3-70b]": {"model": "snowflake-llama-3.3-70b", "max_tokens": 4096} 
      }

