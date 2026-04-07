from typing import Dict, Any, Optional


class BaseNode:
    node_name: str
    node_id: str
    config: Dict[str, Any]
    node_intro: str
    node_type: str
