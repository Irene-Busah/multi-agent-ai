import time

from .clients import openai

TERMINAL = ("completed", "incomplete", "failed", "cancelled")


def wait(response, deadline_s=600, every_s=2):
    """Poll a background response until it reaches a terminal status (or the deadline cancels it)."""
    started = time.monotonic()
    while response.status not in TERMINAL:
        if time.monotonic() - started > deadline_s:
            return openai.responses.cancel(response.id)
        time.sleep(every_s)
        response = openai.responses.retrieve(response.id)
    return response


def final_text(response):
    """The answer text. gpt-5.4 can return the same message twice, phase "commentary" and "final_answer";
    output_text joins both, so keep the final answer when the model marks one."""
    finals = [item for item in response.output if item.type == "message" and getattr(item, "phase", None) == "final_answer"]
    if not finals:
        return response.output_text
    return "".join(part.text for item in finals for part in item.content if part.type == "output_text")
