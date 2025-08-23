import pytest
import json
import uuid
import os
import shutil
from pathlib import Path
from PAI.resources.resource_registry import ResourceRegistry


@pytest.fixture
def test_dir(tmp_path):
    """Create a test directory for resources"""
    resources_dir = tmp_path / "test_resources"
    resources_dir.mkdir()
    resources_file = resources_dir / "resources.json"

    with open(resources_file, "w") as f:
        json.dump({"resources": []}, f)

    original_prepare = ResourceRegistry._prepare_path

    def mock_prepare_path(cls, path=None):
        if path is None:
            return resources_file
        return path

    ResourceRegistry._prepare_path = classmethod(mock_prepare_path)

    yield resources_dir

    ResourceRegistry._prepare_path = original_prepare


def test_resource_registry_create_resource_1(test_dir):
    """Test creating a new resource successfully"""
    result = ResourceRegistry.create_resource(
        Name="new_resource",
        content="Test content",
        Description="Test description",
        ContentType="text",
    )

    assert result is not None
    assert result["Name"] == "new_resource"
    assert result["Description"] == "Test description"
    assert "ID" in result

    resources = ResourceRegistry.get_resources()
    assert len(resources["resources"]) == 1
    assert resources["resources"][0]["Name"] == "new_resource"


def test_resource_registry_create_resource_2(test_dir):
    """Test attempting to create a resource with a name that already exists"""

    ResourceRegistry.create_resource(
        Name="existing_resource", content="Test content", Description="Test description"
    )

    result = ResourceRegistry.create_resource(
        Name="existing_resource",
        content="Different content",
        Description="Different description",
    )

    assert result is None


def test_resource_registry_create_resource_3(test_dir):
    """Test creating a resource with a file that doesn't exist"""

    with pytest.raises(FileNotFoundError):
        ResourceRegistry.create_resource(
            Name="file_resource",
            content=str(test_dir / "nonexistent_file.txt"),
            Description="Test description",
            ContentType="file",
            local_file=True,
        )


def test_resource_registry_update_resource_1(test_dir):
    """Test updating an existing resource successfully"""

    ResourceRegistry.create_resource(
        Name="update_test",
        content="Original content",
        Description="Original description",
        ContentType="text",
    )

    result = ResourceRegistry.update_resource(
        Name="update_test", content="Updated content", Description="Updated description"
    )

    assert result is not None
    assert result["Description"] == "Updated description"
    assert result["Content"] == "Updated content"

    updated = ResourceRegistry.get_resource(Name="update_test")
    assert updated["Content"] == "Updated content"


def test_resource_registry_delete_resource_1(test_dir):
    """Test deleting an existing resource successfully"""

    ResourceRegistry.create_resource(
        Name="delete_test", content="Test content", Description="Test description"
    )

    resources_before = ResourceRegistry.get_resources()
    assert any(r["Name"] == "delete_test" for r in resources_before["resources"])

    result = ResourceRegistry.delete_resource(Name="delete_test")

    assert result is True

    resources_after = ResourceRegistry.get_resources()
    assert not any(r["Name"] == "delete_test" for r in resources_after["resources"])


def test_resource_registry_get_resources_1(test_dir):
    """Test retrieving all resources successfully"""
    ResourceRegistry.create_resource(
        Name="resource1", content="Content 1", Description="Description 1"
    )

    ResourceRegistry.create_resource(
        Name="resource2", content="Content 2", Description="Description 2"
    )

    result = ResourceRegistry.get_resources()

    assert result is not None
    assert "resources" in result
    assert len(result["resources"]) == 2
    names = [r["Name"] for r in result["resources"]]
    assert "resource1" in names
    assert "resource2" in names


def test_resource_registry_get_resource_1(test_dir):
    """Test retrieving a specific resource by name successfully"""

    ResourceRegistry.create_resource(
        Name="get_test", content="Test content", Description="Test description"
    )

    result = ResourceRegistry.get_resource(Name="get_test")

    assert result is not None
    assert result["Name"] == "get_test"
    assert result["Content"] == "Test content"
    assert result["Description"] == "Test description"


def test_resource_registry_get_toolmetadata_1(test_dir):
    """Test retrieving metadata for all resources"""
    ResourceRegistry.create_resource(
        Name="metadata_test",
        content="Sensitive content",
        Description="Test description",
        Tags=["test", "metadata"],
    )

    result = ResourceRegistry.get_tool_metadata()

    assert result is not None
    assert len(result) == 1
    assert result[0]["Name"] == "metadata_test"
    assert result[0]["Description"] == "Test description"
    assert "Content" not in result[0]
    assert "Tags" in result[0]
    assert len(result[0]["Tags"]) == 2
