import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MODEL = os.environ["MODEL_DEPLOYMENT_NAME"]
CRITIC = os.environ.get("CRITIC_MODEL", MODEL)
CLAIM = os.environ.get("CLAIM_ID", "CLM-77412")
POLICY = "VM-2291"

credential = DefaultAzureCredential()
# Admin client: agents and versions
project = AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential)
# Runtime client: conversations and responses
openai = project.get_openai_client()
# Durable state: Cosmos DB, database "larkspur", containers partitioned by /sessionId (the claim)
cosmos_db = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential).get_database_client(
    os.environ.get("COSMOS_DATABASE", "larkspur"))
runs = cosmos_db.get_container_client("runs")
checkpoints = cosmos_db.get_container_client("checkpoints")
