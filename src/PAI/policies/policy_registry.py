from typing import Dict, Optional, List, Any
from pathlib import Path
import json
from datetime import datetime

from PAI.utils.logger import logger

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
                "Policy_ID": None,
                "Description": Description,
                "Policy_Type": Policy_Type,
                "Regex": Regex if Regex is not None else None,
                "Instructions": Instructions if Instructions is not None else None, 
                "Ruleset_Name": Ruleset_Name if Ruleset_Name is not None else None,  
                "Ruleset_ID": Ruleset_Name if Ruleset_Name is not None else None,
                "LastModified": datetime
            }
            path = cls._prepare_path(path)
            policies = cls.get_policies(path)

            policies.setdefault("policies", []).append(policy_entry)


            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(policies, f, indent=2)

            logger.info(f"Resource '{Name}' (ID: {policies}) added successfully")
            return policy_entry 

        except Exception as e:
            logger.error(f"Error creating policy '{Name}': {e}")
            return None

    @classmethod
    def update_policy(
        cls,
        Name: str,
        Description: str = None,
        Regex: Optional[str] = None,
        Instructions: Optional[str] = None,
        Ruleset_Name: Optional[List[Dict[str, Any]]] = None,
        Ruleset_ID: Optional[List[int]] = None,
        path: Optional[Path] = None,
        ):

        path = cls._prepare_path(path)
        policies = cls.get_policies(path)
        policies_list = policies.get("policies", [])
        policy_found = False

        try:
            for i, policies in enumerate(policies_list):
                if policies.get("Name") == Name:
                    logger.info(f"Policies found: {Name} (ID: {policies.get('ID')})")
                    policy_found = True

                    policies_list[i].update(
                        {
                            "Description": Description,
                            "Regex": Regex,
                            "Instructions": Instructions,
                            "Ruleset_Name": Ruleset_Name,
                            "Ruleset_ID": Ruleset_ID,
                            "LastModified": datetime,
            
                        }
                    )

                    updated_policies = policies_list[i]
                    break

            if not policy_found:
                logger.error(f"Policy not found with Name='{Name}'")
                raise FileNotFoundError("Policy not found")

            path = cls._prepare_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(policies, f, indent=2)
                logger.info(f"Policy '{Name}' updated successfully")
                return updated_policies

        except Exception as e:
            logger.error(f"Error updating policy '{Name}': {e}")
            raise

    @classmethod
    def delete_policy(
        cls, Name: str, path: Optional[Path] = None
    ) -> bool:
        """Delete a specific policy by name."""

        path = cls._prepare_path(path)
        policies = cls.get_policies(path)
        policies_list = policies.get("policies", [])
        initial_count = len(policies_list)
        policy_found = False

        for i, policy in enumerate(policies_list):
            if Name and policy.get("Name") == Name:
                logger.info(
                    f"Resource found: {policy.get('Name')} (ID: {policy.get('ID')})"
                )
                policies_list.pop(i)
                policy_found = True
                break

        if not policy_found:
            logger.error(f"Policy not found with Name='{Name}'")
            raise FileNotFoundError("Policy not found")

        policies["policies"] = policies_list

        path = cls._prepare_path(path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(policies, f, indent=2)

            logger.info(
                f"Resource deleted successfully. Policies count: {initial_count} → {len(policies_list)}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving Policies after deletion: {e}")
            raise

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
        """Return all policies from the registry."""

        path = cls._prepare_path(path)
        policies = {"policies": []}

        if not path.exists():
            logger.debug(
                f"Policies file not found at {path}, returning empty policies"
            )
            return policies

        try:
            with open(path, "r", encoding="utf-8") as f:
                policies = f.read().strip()
                return json.loads(policies) 

        except Exception as e:
            logger.error(f"Error accessing policy location {path}: {e}")
            raise

    @classmethod
    def get_policies_metadata(cls):
        """
        Return instructions of all policies from the registry. Only supports soft policies for now.
        """

        path = cls._prepare_path(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                policies = f.read().strip()
                policies = json.loads(policies) 
                policy_metadata = policies.get("Instructions", [])
                return policy_metadata
        except Exception as e:
            logger.error(f"Error accessing policy location {path}: {e}")
            raise
