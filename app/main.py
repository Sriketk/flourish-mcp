from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType


# Import routers using relative import
from routers import flourish_strains, nabis_strains

# Create FastAPI app with metadata
app = FastAPI(
    title="Flourish MCP API",
    version="1.0.0",
    description="API for managing cannabis strains"
)

# Include routers
app.include_router(flourish_strains.router)
app.include_router(nabis_strains.router)    
# Convert FastAPI app to MCP server with custom configuration
mcp = FastMCP.from_fastapi(
    app=app,
    name="Flourish MCP Server",
    timeout=30.0,  # 30 second timeout for all requests
    route_maps=[
        # All strain endpoints become tools
        RouteMap(
            pattern=r"^/flourish/strains/.*",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            pattern=r"^/nabis/strains/.*",
            mcp_type=MCPType.TOOL,
        ),  
    ],
    mcp_names={
        "get_flourish_strains": "list_flourish_strains",
        "get_flourish_strain_by_id": "get_flourish_strain",
        "post_flourish_strain": "create_flourish_strain",
        "get_nabis_strains": "list_nabis_strains",
        "get_nabis_strain_by_id": "get_nabis_strain",
        "post_nabis_strain": "create_nabis_strain",
    }
)

mcp

if __name__ == "__main__":
    mcp.run()  # Run as MCP server