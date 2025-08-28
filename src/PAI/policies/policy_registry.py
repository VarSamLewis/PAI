from typing import Dict, Optional, List, Any
from pathlib import Path
import json
from datetime import datetime

from PAI.utils.logger import logger
from PAI.utils.registry_utils import _gen_test_identity

class PolicyRegistry:

    @classmethod
    def create_policy(
            cls,
            Name: str,
            Description: str,
            Policy_Type: str,
            Regex: Optional[str] = None,
            Instructions: Optional[str] = None,
            Ruleset_Name: Optional[List[Dict[str, Any]]] = None,
            Ruleset_ID: Optional[List[int]] = None,
            path: Optional[Path] = None,

        ) -> Optional[Dict[str, Any]]:

        if Policy_Type.lower() not in ["hard", "soft"]:
            raise ValueError("Policy_Type must be either 'hard' or 'soft', case nonsensitive.")
        if Policy_Type.lower() == "hard" and not Regex:
            raise ValueError("Regex must be provided for 'hard' policies.")
        if Policy_Type.lower() == "soft" and not Instructions:
            raise ValueError("Instructions must be provided for 'soft' policies.")

        try:

            policy_entry = {
                "Policy_Name": Name,
                "Policy_ID": _gen_test_identity(),
                "Description": Description,
                "Policy_Type": Policy_Type,
                "Regex": Regex if Regex is not None else None,
                "Instructions": Instructions if Instructions is not None else None, 
                "Ruleset_Name": Ruleset_Name if Ruleset_Name is not None else None,  
                "Ruleset_ID": Ruleset_Name if Ruleset_Name is not None else None,
                "LastModifiedDT": datetime
            }

            policies = cls.get_policies(path)

            policies.setdefault("resources", []).append(policy_entry)

            path = cls._prepare_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(policies, f, indent=2)

            logger.info(f"Resource '{Name}' (ID: {policies}) added successfully")
            return policy_entry 

        except Exception as e:
            logger.error(f"Error creating policy '{Name}': {e}")
            return None

    @classmethod
    def _prepare_path(cls, path: Optional[Path] = None) -> Path:
        """Prepare and return the path to the policies registry file."""

        if not path:
            module_dir = Path(__file__).parent.absolute()
            path = module_dir.joinpath("policies.json")

        logger.debug(f"Accessing policies at: {path}")
        return path

    @classmethod
    def get_policies(
        cls, path: Optional[Path] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Return all resources from the registry."""

        path = cls._prepare_path(path)
        resources = {"resources": []}

        if not path.exists():
            logger.debug(
                f"Resources file not found at {path}, returning empty resources"
            )
            return resources

        try:
            with open(path, "r", encoding="utf-8") as f:
                policies = f.read().strip()
                return json.loads(policies) 
                
        except Exception as e:
            logger.error(f"Error accessing resource location {path}: {e}")
            raise