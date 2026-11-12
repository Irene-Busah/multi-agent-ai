"""Part 1: one background run, polled to a terminal status, recorded in Cosmos DB."""
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.clients import CLAIM, MODEL, cosmos_db, openai  # noqa: E402
from common.claims import get_fnol  # noqa: E402

runs = cosmos_db.get_container_client("runs")
BUDGET = {"seconds": 600, "input_tokens": 100_000}
FNOL = get_fnol(CLAIM)                       # the broker's PDF, as text
started = time.monotonic()

# 1. Start the run in the background and keep the id: your handle to poll, cancel and reconnect
response = openai.responses.create(
    model=MODEL, background=True, max_output_tokens=4_000,
    input=f"You are Larkspur Mutual's claims assessor. Outline the assessment steps for this loss, "
          f"and list the documents you would need.\n\n{FNOL}")
run = {"id": response.id, "sessionId": CLAIM, "type": "run", "transitions": [response.status]}
print("started", response.id, response.status)

# 2. Poll until the status is terminal; cancel at the deadline; record every status change
while response.status in ("queued", "in_progress"):
    if time.monotonic() - started > BUDGET["seconds"]:
        response = openai.responses.cancel(response.id)
        break
    time.sleep(2)
    response = openai.responses.retrieve(response.id)
    if response.status != run["transitions"][-1]:
        run["transitions"].append(response.status)

# 3. Map the terminal status to an action and write the run record
run["status"] = response.status
run["seconds"] = round(time.monotonic() - started, 1)
if response.status == "completed":
    run["input_tokens"] = response.usage.input_tokens
    run["output_tokens"] = response.usage.output_tokens
    run["within_budget"] = run["input_tokens"] <= BUDGET["input_tokens"]
elif response.status == "incomplete":
    run["reason"] = response.incomplete_details.reason      # raise max_output_tokens or split the step
elif response.status == "failed":
    run["reason"] = response.error.code                     # rate_limit_exceeded: back off; invalid_prompt: fix it
runs.upsert_item(run)

print(" -> ".join(run["transitions"]), run.get("reason", ""))
if response.status == "completed":
    print(response.output_text[:800])
