from flask import Blueprint, jsonify, request, Response, current_app
import requests
import json
from config import Config

api_bp = Blueprint('/v1', __name__)

def transform_request(openai_request):
    """
    Transforms an OpenAI-like request into a Snowflake-compatible request.
    """
    transformed_request = {
        "model": Config.SNOWFLAKE_LLM_MODELS[openai_request.get("model", "snowflake[claude-3-5-sonnet]")]["model"],
        "messages": openai_request.get("messages", []),
        "temperature": openai_request.get("temperature", 0.7),
        "top_p": openai_request.get("top_p", 1),
        "max_tokens": openai_request.get("max_tokens", 4096)
    }
   
    print (f'VENU: transformed_request is: <{transformed_request}>')
    return transformed_request


def transform_response(snowflake_response):
    """
    Transforms a Snowflake API response into an OpenAI-compatible response format.
    """
    return {
        "id": snowflake_response.get("id"),
        "created": snowflake_response.get("created"),
        "model": snowflake_response.get("model"),
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": choice.get("delta", {}).get("content", "")
                }
            }
            for choice in snowflake_response.get("choices", [])
            if "delta" in choice
        ],
        "usage": snowflake_response.get("usage", {})
    }

@api_bp.route("/models", methods=["GET"])
def models():
    models_list = []

    for model in Config.SNOWFLAKE_LLM_MODELS.keys():
      models_list.append({"id": model, "object": "model", "created": 1700000000, "owned_by": "snowflake-hosted"})

    return jsonify({
        "object": "list",
        "data": models_list
    }), 200

@api_bp.route("/chat/completions", methods=["POST"])
def convert():
    openai_request = request.json
    if not openai_request:
        return jsonify({"error": "Invalid request"}), 400

    snowflake_request = transform_request(openai_request)

    headers = {
        "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT",
        "Authorization": f"Bearer {current_app.config.get('SNOWFLAKE_AUTH_TOKEN')}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    print (f'VENU: convert.headers is: <{headers}>')

    response = requests.post(
        f'{current_app.config.get("SNOWFLAKE_API_URL")}/api/v2/cortex/inference:complete',
        json=snowflake_request,
        headers=headers,
        stream=True
    )
    #print (f'VENU: convert.response.text is: <{response.text}>')

    if response.headers.get('Content-Type', '').startswith('text/event-stream'):
        def event_stream():
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8").replace("data: ", "").strip()
                    if decoded_line:
                        yield f"data: {json.dumps(transform_response(json.loads(decoded_line)))}\n\n"
        return Response(event_stream(), mimetype='text/event-stream')

    response_data = response.json()
    return jsonify(transform_response(response_data)) if response.status_code == 200 else jsonify({"error": "Failed to retrieve response", "details": response_data}), response.status_code

