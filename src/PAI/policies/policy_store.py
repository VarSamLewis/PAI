from pathlib import Path
from .policy_registry import PolicyRegistry

PolicyRegistry.create_policy(
    Name="Don't be evil",
    Description="Soft promt to tell the AI to be not evil",
    Policy_Type="soft",
    Regex=None,
    Instructions="Don't be malicious",
    Ruleset_Name="Standard",
    Ruleset_ID=1,   
)   