"""Function tools for the claims assessor. The model never runs code; your code does."""
import csv
import json
import uuid
from email import policy as email_policy
from email.parser import BytesParser
from pathlib import Path

from azure.ai.projects.models import FunctionTool
from pypdf import PdfReader

DATA = Path(__file__).resolve().parents[1] / "data"


def text_of(path):
    """A claim file as the model reads it: PDF (brokers, adjusters, wordings), email, or plain text and JSON."""
    if path.suffix == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if path.suffix == ".eml":
        mail = BytesParser(policy=email_policy.default).parse(path.open("rb"))
        body = mail.get_body(("plain",)).get_content()
        return f"From: {mail['from']}\nDate: {mail['date']}\nSubject: {mail['subject']}\n\n{body}"
    return path.read_text(encoding="utf-8")


def _read(folder, stem):
    """The file data/<folder>/<stem>.<any extension>: the format is whatever the sender used."""
    for path in sorted((DATA / folder).glob(f"{stem}.*")):
        return text_of(path)
    return f"Not found: {folder}/{stem}"


def get_policy(policy_id: str) -> str:
    return _read("policies", policy_id)


def get_fnol(claim_id: str) -> str:
    return _read("claims", f"{claim_id}-fnol")


def get_adjuster_report(claim_id: str) -> str:
    return _read("adjuster", f"{claim_id}-site-report")


def get_repair_quotes(claim_id: str) -> str:
    path = DATA / "quotes" / f"{claim_id}-quotes.csv"
    if not path.exists():
        return f"No quotes for {claim_id}"
    with path.open(encoding="utf-8") as f:
        return json.dumps(list(csv.DictReader(f)))


def get_business_interruption(claim_id: str) -> str:
    path = DATA / "bi" / f"{claim_id}-business-interruption.csv"
    if not path.exists():
        return f"No business-interruption data for {claim_id}"
    with path.open(encoding="utf-8") as f:
        return json.dumps(list(csv.DictReader(f)))


def record_fnol(policy_id: str, description: str) -> str:
    """Intake tool (section 6): record a first notice of loss and return the claim number."""
    claim_id = f"CLM-{uuid.uuid4().int % 90000 + 10000}"
    out = DATA / "claims" / f"{claim_id}-fnol.txt"            # the intake record, plain text
    out.write_text(f"First notice of loss · {claim_id}\nPolicy: {policy_id}\nEvent: {description}\n", encoding="utf-8")
    return json.dumps({"claim_id": claim_id, "status": "recorded"})


def _tool(name, description, /, **props):
    return FunctionTool(name=name, description=description,
                        parameters={"type": "object", "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
                                    "required": list(props)})


get_policy_tool = _tool("get_policy", "Policy wording, sums insured, deductibles and conditions for a Larkspur policy number, format VM-####", policy_id="Policy number")
get_adjuster_report_tool = _tool("get_adjuster_report", "Adjuster site report for a claim number, format CLM-#####", claim_id="Claim number")
get_repair_quotes_tool = _tool("get_repair_quotes", "Contractor quotes (JSON rows) for a claim number", claim_id="Claim number")
get_business_interruption_tool = _tool("get_business_interruption", "Weekly business-interruption figures (JSON rows) for a claim number", claim_id="Claim number")
record_fnol_tool = _tool("record_fnol", "Record a first notice of loss for a policy and return the claim number", policy_id="Policy number", description="What happened, where and when")

ASSESSOR_TOOLS = [get_policy_tool, get_adjuster_report_tool, get_repair_quotes_tool, get_business_interruption_tool]
FUNCTIONS = {"get_policy": get_policy, "get_adjuster_report": get_adjuster_report, "get_repair_quotes": get_repair_quotes,
             "get_business_interruption": get_business_interruption, "record_fnol": record_fnol}


def run_tool(call):
    """Run one function_call item and return its output text."""
    return FUNCTIONS[call.name](**json.loads(call.arguments))


def evidence(claim_id: str, policy_id: str) -> str:
    """Everything the assessor needs, as one text block (sections 3 to 5 send it directly)."""
    return "\n\n".join([
        "## First notice of loss\n" + get_fnol(claim_id),
        "## Policy\n" + get_policy(policy_id),
        "## Adjuster report\n" + get_adjuster_report(claim_id),
        "## Quotes\n" + get_repair_quotes(claim_id),
        "## Business interruption\n" + get_business_interruption(claim_id),
    ])
