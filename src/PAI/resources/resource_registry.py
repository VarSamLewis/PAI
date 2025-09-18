import json
import datetime
from typing import Optional, List, Dict, Any, Union
import uuid
from pathlib import Path
from .resource_validator import Resource, ResourceCollection

from PAI.utils.logger import logger


class ResourceRegistry:
    """
    Registry for managing resources.
    """

    @classmethod
    def create_resource(
        cls,
        Name: str,
        Description: str,
        Content: Optional[str] = None,
        content: Optional[str] = None,  # deprecated alias
        ContentType: Optional[str] = None,
        local_file: bool = False,
        Filetype: Optional[str] = None,
        Tags: Optional[List[str]] = None,
        path: Optional[Path] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new resource and add it to the registry."""

        try:
            try:
                if cls._check_resource_exist(Name):
                    logger.info(
                        f"Resource with Name='{Name}' already exists. Skipping creation."
                    )
                    return None
            except Exception:
                pass

            logger.info(f"Adding resource: {Name}")

            # Normalize deprecated 'content' param to 'Content'
            if Content is None and content is not None:
                logger.warning(
                    "Parameter 'content' is deprecated. Use 'Content' instead."
                )
                Content = content

            if ContentType:
                Content = cls._handle_Content_type(
                    Content or "", ContentType, local_file
                )

            resource_id = str(uuid.uuid4())
            size = cls._get_resource_size(Content or "")

            resource_entry = Resource(
                Name=Name,
                ID=resource_id,
                Description=Description,
                ContentType=ContentType,
                Content=Content or "",
                Size=size,
                Filetype=Filetype,
                Tags=Tags,
            ).model_dump()

            resources = cls.get_resources(path)

            resources.setdefault("resources", []).append(resource_entry)

            path = cls._prepare_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(resources, f, indent=2)

            logger.info(f"Resource '{Name}' (ID: {resource_id}) added successfully")
            return resource_entry

        except Exception as e:
            logger.error(f"Error adding resource '{Name}': {e}")
            raise

    @classmethod
    def update_resource(
        cls,
        Name: str,
        Description: str,
        Content: Optional[str] = None,
        content: Optional[str] = None,  # deprecated alias
        ContentType: Optional[str] = None,
        local_file: bool = False,
        Filetype: Optional[str] = None,
        Tags: Optional[List[str]] = None,
        path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Update an existing resource in the registry."""

        resources = cls.get_resources(path)
        resources_list = resources.get("resources", [])
        resource_found = False

        # Normalize deprecated 'content' param to 'Content'
        if Content is None and content is not None:
            logger.warning("Parameter 'content' is deprecated. Use 'Content' instead.")
            Content = content

        if ContentType:
            Content = cls._handle_Content_type(Content or "", ContentType, local_file)

        size = cls._get_resource_size(Content or "")

        try:
            for i, resource in enumerate(resources_list):
                if resource.get("Name") == Name:
                    logger.info(f"Resource found: {Name} (ID: {resource.get('ID')})")
                    resource_found = True

                    resources_list[i].update(
                        {
                            "Description": Description,
                            "Content": Content or "",
                            "Size": size,
                            "LastModified": datetime.datetime.now().isoformat(),
                            "ContentType": (
                                ContentType
                                if ContentType
                                else resources_list[i].get("ContentType")
                            ),
                            "Filetype": (
                                Filetype
                                if Filetype
                                else resources_list[i].get("Filetype")
                            ),
                            "Tags": Tags if Tags else resources_list[i].get("Tags"),
                        }
                    )

                    updated_resource = resources_list[i]
                    break

            if not resource_found:
                logger.error(f"Resource not found with Name='{Name}'")
                raise FileNotFoundError("Resource not found")

            path = cls._prepare_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(resources, f, indent=2)
                logger.info(f"Resource '{Name}' updated successfully")
                return updated_resource

        except Exception as e:
            logger.error(f"Error updating resource '{Name}': {e}")
            raise

    @classmethod
    def delete_resource(
        cls, Name: str, ID: Optional[str] = None, path: Optional[Path] = None
    ) -> bool:
        """Delete a specific resource by name or ID."""

        resources = cls.get_resources(path)
        resources_list = resources.get("resources", [])
        initial_count = len(resources_list)
        resource_found = False

        for i, resource in enumerate(resources_list):
            if (Name and resource.get("Name") == Name) or (
                ID and resource.get("ID") == ID
            ):
                logger.info(
                    f"Resource found: {resource.get('Name')} (ID: {resource.get('ID')})"
                )
                resources_list.pop(i)
                resource_found = True
                break
        if not resource_found:
            logger.error(f"Resource not found with Name='{Name}' ID='{ID}'")
            raise FileNotFoundError("Resource not found")

        resources["resources"] = resources_list

        path = cls._prepare_path(path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(resources, f, indent=2)

            logger.info(
                f"Resource deleted successfully. Resources count: {initial_count} → {len(resources_list)}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving resources after deletion: {e}")
            raise

    @classmethod
    def get_resource(
        cls, Name: str, ID: Optional[str] = None, path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Get a specific resource by name or ID"""

        resources = cls.get_resources(path)

        for resource in resources.get("resources", []):
            if (Name and resource.get("Name") == Name) or (
                ID and resource.get("ID") == ID
            ):
                # Resolve linked content on read, if applicable
                ct = resource.get("ContentType")
                if isinstance(ct, str):
                    ct_lower = ct.lower()
                    if ct_lower in {"file", "url"}:
                        original = resource.get("Content")
                        try:
                            is_local_file = False
                            if ct_lower == "file":
                                try:
                                    p = Path(str(original))
                                    is_local_file = p.exists() and p.is_file()
                                except Exception:
                                    is_local_file = False

                            resolved = cls._handle_Content_type(
                                original or "",
                                ct,
                                local_file=is_local_file,
                            )
                            resource["Content"] = resolved
                        except Exception as e:
                            logger.warning(
                                f"Failed to resolve linked content for resource '{resource.get('Name')}': {e}"
                            )

                logger.info(
                    f"Resource found: {resource.get('Name')} (ID: {resource.get('ID')})"
                )
                return resource

        logger.error(f"Resource not found with Name='{Name}' ID='{ID}'")
        raise FileNotFoundError("Resource not found")

    @classmethod
    def get_resources(
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
                content_text = f.read().strip()
                if content_text:
                    try:
                        resources_raw = json.loads(content_text)
                        resources = ResourceCollection.model_validate(
                            resources_raw
                        ).model_dump()
                        logger.debug(
                            f"Loaded {len(resources.get('resources', []))} resources"
                        )
                    except Exception as validation_error:
                        logger.error(f"Resource validation error: {validation_error}")
                        raise
                else:
                    logger.debug(
                        "Empty resources file, returning default empty structure"
                    )
            return resources

        except json.JSONDecodeError:
            logger.warning(
                f"Invalid JSON in resource file: {path}, returning empty resources"
            )
            return resources
        except Exception as e:
            logger.error(f"Error accessing resource location {path}: {e}")
            raise

    @classmethod
    def get_resource_metadata(cls, path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Get metadata for all resources except their Content."""

        resources = cls.get_resources(path)

        metadata = [
            {k: v for k, v in resource.items() if k != "Content"}
            for resource in resources.get("resources", [])
        ]

        logger.debug(f"Retrieved metadata for {len(metadata)} resources")
        return metadata

    @classmethod
    def _check_resource_exist(cls, Name: str) -> bool:
        """Check if a resource with the given name exists."""

        resources = cls.get_resources()
        for resource in resources.get("resources", []):
            if Name and resource.get("Name") == Name:
                return True
        return False

    @classmethod
    def _prepare_path(cls, path: Optional[Path] = None) -> Path:
        """Prepare and return the path to the resource registry file."""

        if not path:
            module_dir = Path(__file__).parent.absolute()
            path = module_dir.joinpath("resources.json")

        logger.debug(f"Accessing resources at: {path}")
        return path

    @classmethod
    def _get_resource_size(cls, Content: str) -> float:
        """Calculate the size of the resource Content in megabytes."""

        if not Content:
            logger.debug("Empty Content, returning size 0.0")
            return 0.0

        byte_size = len(Content.encode("utf-8"))
        mb_size = byte_size / (1024 * 1024)

        logger.debug(f"Content size: {byte_size} bytes ({mb_size} MB)")
        return round(mb_size, 2)

    @classmethod
    def _handle_Content_type(
        cls, Content: str, ContentType: str, local_file: bool
    ) -> str:
        """Handle Content based on its type and source."""
        if not isinstance(ContentType, str):
            return Content

        ct = ContentType.lower()

        if ct == "file":
            if local_file:
                try:
                    logger.debug(f"Reading Content from file: {Content}")
                    with open(Path(Content), "r", encoding="utf-8") as f:
                        Content = f.read()
                    logger.debug(
                        f"File read successfully, Content length: {len(Content)}"
                    )
                except FileNotFoundError:
                    logger.error(f"File not found: {Content}")
                    raise FileNotFoundError(f"Resource file not found: {Content}")
                except Exception as e:
                    logger.error(f"Error reading file {Content}: {e}")
                    raise
            # Return original value (likely a path) when not local_file
            return Content

        if ct == "url":
            return cls._access_external_file(Content)

        return Content

    @classmethod
    def _access_external_file(
        cls, path: str, credentials: Optional[Dict[str, Any]] = None
    ) -> str:
        """Access and retrieve Content from an external file or URL."""
        import requests
        from urllib.parse import urlparse

        logger.info(f"Accessing external file: {path}")

        try:
            parsed = urlparse(path)

            if parsed.scheme in ["http", "https"]:
                logger.debug(f"Accessing web URL: {path}")

                auth = None
                headers = {}
                if credentials:
                    if "username" in credentials and "password" in credentials:
                        auth = (credentials["username"], credentials["password"])
                    if "headers" in credentials:
                        headers = credentials["headers"]
                    if "token" in credentials:
                        headers["Authorization"] = f"Bearer {credentials['token']}"

                response = requests.get(path, auth=auth, headers=headers, timeout=30)
                response.raise_for_status()
                return response.text
            else:
                logger.error(f"Unsupported file location: {path}")
                raise ValueError(f"Unsupported file location: {path}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading from URL {path}: {e}")
            raise
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied accessing file: {path}")
            raise
        except Exception as e:
            logger.error(f"Error accessing external file {path}: {e}")
            raise
