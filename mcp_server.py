import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer as FastMCP

mcp = FastMCP("CampusPulse MCP")

DATA_FILE = (
    Path(__file__).resolve().parent
    / "campuspulse_agent"
    / "data.json"
)


@mcp.tool()
def get_student_assignments() -> list[dict]:
    """Get student assignments from the academic dataset."""
    with DATA_FILE.open(encoding="utf-8") as file:
        data = json.load(file)

    return data["assignments"]


if __name__ == "__main__":
    mcp.run(transport="stdio")