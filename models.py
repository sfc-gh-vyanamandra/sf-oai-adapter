from extensions import db

class KeyStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.Text, nullable=False, unique=True)
    snowflake_url = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    encrypted_private_key = db.Column(db.Text, nullable=False)
    encrypted_public_key = db.Column(db.Text, nullable=False)

class KeyStorePassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encrypted_password = db.Column(db.Text, nullable=False)

class JWTToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('key_store.id'), nullable=False)
    token = db.Column(db.Text, nullable=False)
    api_url = db.Column(db.Text, nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)

class SnowflakeLLMModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    model = db.Column(db.String(100), nullable=False)
    max_tokens = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

SNOWFLAKE_LLM_MODELS = {
    "snowflake[claude-3-5-sonnet]": {"model": "claude-3-5-sonnet", "max_tokens": 18000, "description": "Claude AI's powerful sonnet model."},
    "snowflake[deepseek-r1]": {"model": "deepseek-r1", "max_tokens": 128000, "description": "Deepseek's advanced retrieval model."},
    "snowflake[gemma-7b]": {"model": "gemma-7b", "max_tokens": 8000, "description": "Gemma's compact 7B model."},
    "snowflake[jamba-1.5-large]": {"model": "jamba-1.5-large", "max_tokens": 256000, "description": "Jamba's large-scale model version 1.5."},
    "snowflake[jamba-1.5-mini]": {"model": "jamba-1.5-mini", "max_tokens": 256000, "description": "Jamba's mini model version 1.5."},
    "snowflake[jamba-instruct]": {"model": "jamba-instruct", "max_tokens": 256000, "description": "Instruction-tuned model from Jamba."},
    "snowflake[llama2-70b-chat]": {"model": "llama2-70b-chat", "max_tokens": 4096, "description": "Meta's LLaMA 2, 70B chat model."},
    "snowflake[llama3-70b]": {"model": "llama3-70b", "max_tokens": 4096, "description": "Meta's LLaMA 3, 70B parameter model."},
    "snowflake[llama3-8b]": {"model": "llama3-8b", "max_tokens": 4096, "description": "Meta's LLaMA 3, 8B parameter model."},
    "snowflake[llama3.1-405b]": {"model": "llama3.1-405b", "max_tokens": 128000, "description": "Enhanced LLaMA 3.1, 405B parameter model."},
    "snowflake[llama3.1-70b]": {"model": "llama3.1-70b", "max_tokens": 128000, "description": "LLaMA 3.1, 70B parameter model."},
    "snowflake[llama3.1-8b]": {"model": "llama3.1-8b", "max_tokens": 128000, "description": "LLaMA 3.1, 8B parameter model."},
    "snowflake[llama3.2-1b]": {"model": "llama3.2-1b", "max_tokens": 128000, "description": "LLaMA 3.2, 1B parameter model."},
    "snowflake[llama3.2-3b]": {"model": "llama3.2-3b", "max_tokens": 128000, "description": "LLaMA 3.2, 3B parameter model."},
    "snowflake[llama3.3-70b]": {"model": "llama3.3-70b", "max_tokens": 4096, "description": "LLaMA 3.3, 70B parameter model."},
    "snowflake[mistral-7b]": {"model": "mistral-7b", "max_tokens": 32000, "description": "Mistral's 7B parameter model."},
    "snowflake[mistral-large]": {"model": "mistral-large", "max_tokens": 32000, "description": "Mistral's large-scale model."},
    "snowflake[mistral-large2]": {"model": "mistral-large2", "max_tokens": 128000, "description": "Second generation of Mistral's large model."},
    "snowflake[mixtral-8x7b]": {"model": "mixtral-8x7b", "max_tokens": 32000, "description": "Mixtral's ensemble model of 8x7B."},
    "snowflake[reka-core]": {"model": "reka-core", "max_tokens": 32000, "description": "Reka's core model."},
    "snowflake[reka-flash]": {"model": "reka-flash", "max_tokens": 100000, "description": "Reka's high-speed model."},
    "snowflake[snowflake-arctic]": {"model": "snowflake-arctic", "max_tokens": 4096, "description": "Snowflake's Arctic model."},
    "snowflake[snowflake-llama-3.1-405b]": {"model": "snowflake-llama-3.1-405b", "max_tokens": 128000, "description": "Snowflake's LLaMA 3.1, 405B parameter model."},
    "snowflake[snowflake-llama-3.3-70b]": {"model": "snowflake-llama-3.3-70b", "max_tokens": 4096, "description": "Snowflake's LLaMA 3.3, 70B parameter model."}
}

def populate_llm_models():
    for name, details in SNOWFLAKE_LLM_MODELS.items():
        if not SnowflakeLLMModel.query.filter_by(name=name).first():
            model_entry = SnowflakeLLMModel(
                name=name,
                model=details["model"],
                max_tokens=details["max_tokens"],
                description=details.get("description", "")
            )
            db.session.add(model_entry)
    db.session.commit()

# Call this function after creating the database
def create_db():
    db.create_all()
    populate_llm_models()

