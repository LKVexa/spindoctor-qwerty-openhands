# Genuine OpenHands Conversation with a loopback model-protocol stand-in.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import uuid
from native_host import isolate, install_copy

def text_content(value):
    if isinstance(value, str):
        return value
    return "\n".join(item.get("text", "") for item in value or [] if isinstance(item, dict))

class ConversationHost:
    def __init__(self, use_incoming_workspace=True):
        self.home = Path(tempfile.mkdtemp(prefix="spindoctor-openhands-conversation-"))
        isolate(self.home)
        if use_incoming_workspace:
            os.environ.setdefault("SPINDOCTOR_WORKSPACE", str(self.home / "workspace"))
        else:
            os.environ["SPINDOCTOR_WORKSPACE"] = str(self.home / "workspace")
        self.root = install_copy(self.home)
        self.provider_requests = []
        self.provider_errors = []
        self.events = []
        self.closed_conversations = 0
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                try:
                    if self.path != "/v1/chat/completions":
                        raise ValueError("Unexpected local provider route: " + self.path)
                    size = int(self.headers.get("Content-Length", "0"))
                    if size < 1 or size > 32 * 1024 * 1024:
                        raise ValueError("Unexpected provider request size")
                    body = json.loads(self.rfile.read(size))
                    messages = body.get("messages", [])
                    last = -1
                    instruction = None
                    for index, item in enumerate(messages):
                        if item.get("role") != "user":
                            continue
                        match = re.search(r"\[SPINDOCTOR-TEST\]([\s\S]*?)\[/SPINDOCTOR-TEST\]", text_content(item.get("content")))
                        if match:
                            last = index
                            instruction = json.loads(match.group(1))
                    if instruction is None:
                        raise ValueError("Missing deterministic test instruction")
                    schemas = body.get("tools", [])
                    names = [item.get("function", {}).get("name") for item in schemas]
                    completed = any(item.get("role") == "tool" for item in messages[last + 1:])
                    name = "finish" if completed else instruction["name"]
                    arguments = {"message": "Local integration test completed."} if completed else instruction["arguments"]
                    if name not in names:
                        raise ValueError("Requested host tool missing from actual provider schemas: " + name)
                    owner.provider_requests.append({"requested": instruction["name"], "completed": completed, "schemas": schemas})
                    response = {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion", "created": 0, "model": "gpt-4o",
                                "choices": [{"index": 0, "message": {"role": "assistant", "content": None, "tool_calls": [{"id": "call_" + uuid.uuid4().hex, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}]}, "finish_reason": "tool_calls"}],
                                "usage": {"prompt_tokens": 64, "completion_tokens": 12, "total_tokens": 76}}
                    payload = json.dumps(response).encode("utf-8")
                    self.send_response(200)
                except Exception as error:
                    owner.provider_errors.append(str(error))
                    payload = json.dumps({"error": {"message": str(error)}}).encode("utf-8")
                    self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        from openhands.sdk import LLM
        self.llm = LLM(model="openai/gpt-4o", base_url="http://127.0.0.1:" + str(self.server.server_port) + "/v1", api_key="test", api_mode="chat", stream=False, num_retries=0, caching_prompt=False, reasoning_effort=None, max_input_tokens=128000, max_output_tokens=4096)
        self.last_conversation = None

    def call(self, name, arguments):
        from openhands.sdk import Agent, Conversation
        from openhands.sdk.plugin import PluginSource
        from openhands.sdk.event import ObservationEvent
        events = []
        project = self.home / "project"
        project.mkdir(exist_ok=True)
        conversation = Conversation(Agent(llm=self.llm, tools=[], include_default_tools=["FinishTool"]), workspace=project,
                                    plugins=[PluginSource(source=str(self.root))], persistence_dir=self.home / "conversations",
                                    visualizer=None, delete_on_close=False, max_iteration_per_run=4, callbacks=[events.append])
        self.last_conversation = conversation
        try:
            instruction = {"name": name, "arguments": arguments}
            conversation.send_message("[SPINDOCTOR-TEST]" + json.dumps(instruction) + "[/SPINDOCTOR-TEST]")
            conversation.run()
            observations = [event.observation for event in events if isinstance(event, ObservationEvent) and event.tool_name == name]
            if len(observations) != 1:
                raise ValueError("Genuine Conversation did not produce exactly one requested observation: " + str([type(event).__name__ for event in events]))
            observation = observations[0]
            header = "[Tool '" + name + "' executed.]"
            text = "\n".join(block.text for block in observation.content if hasattr(block, "text") and block.text != header)
            result = {"ok": not observation.is_error, "markdown": text} if name.endswith("spindoctor_functions") else json.loads(text)
            self.events.extend(events)
            return result, text, observation
        finally:
            conversation.close()
            self.closed_conversations += 1

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=10)
        (self.home / "provider-receipt.json").write_text(json.dumps({"requests": self.provider_requests, "errors": self.provider_errors, "closedConversations": self.closed_conversations}, indent=2) + "\n", encoding="utf-8")
