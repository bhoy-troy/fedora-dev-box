#!/usr/bin/python3

import click
import filecmp
import hashlib
import logging
import os
import subprocess
import sys
import yaml

from pathlib import Path


logger = logging.getLogger(__name__)


class BindMountError(Exception):
    pass


default_bind_mounts_cfg = (
    Path.home() / ".config" / "rhel-developer-toolbox" / "config" / "bind_mounts.yaml"
)


def get_file_hash(filepath, block_size=65536):
    """Generates a SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def have_different_contents(dir1, dir2):
    """
    Checks if two directories have different contents using a fail-fast approach.
    Returns True if they are different, False if they are the same.
    """
    # Create iterators for both directory trees
    walker1 = os.walk(dir1)
    walker2 = os.walk(dir2)

    for root1, dirs1, files1 in walker1:
        # Get the next level of the directory tree from both iterators
        try:
            root2, dirs2, files2 = next(walker2)
        except StopIteration:
            # If one iterator is exhausted, and the other is not, they must be
            # different sizes.
            return True

        # Check for different directory lists (sorted to handle order differences)
        if sorted(dirs1) != sorted(dirs2):
            return True

        # Check for different file lists (sorted)
        if sorted(files1) != sorted(files2):
            return True

        # Now, check the contents of common files
        for filename in files1:
            # Get full paths
            path1 = os.path.join(root1, filename)
            path2 = os.path.join(root2, filename)

            # Check for size difference first (fast)
            try:
                size1 = os.stat(path1).st_size
                size2 = os.stat(path2).st_size
            except FileNotFoundError:
                # Should not happen if lists are the same, but good practice
                return True

            if size1 != size2:
                return True

            # Check for content difference using a hash (more reliable)
            if get_file_hash(path1) != get_file_hash(path2):
                return True
    try:
        next(walker2)
    except StopIteration:
        return False  # Both iterators are exhausted, so they must be the same

    # If we get here, walker2 was not exhausted, so they must be different
    return True


def bind_mount_file(source, destination, options=[]):
    if not filecmp.cmp(source, destination, shallow=True):
        # Invoke the 'mount' command to bind mount the file
        bind_options = ["bind"] + options
        try:
            result = subprocess.run(
                ["mount", "-o", ",".join(bind_options), source, destination],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.debug(f"Mount command output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error binding {source} to {destination}: {e}")
            raise BindMountError(f"Error binding {source} to {destination}: {e}")
    else:
        logger.info(f"Source {source} and destination {destination} are the same")
        return


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="WARNING",
    show_default=True,
)
@click.argument(
    "bind_mounts_config", type=click.Path(), default=default_bind_mounts_cfg
)
def main(log_level, bind_mounts_config):
    logging.basicConfig(
        format="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
        level=log_level,
    )
    logger.debug("Debug logging enabled")

    bind_mounts_config = Path(bind_mounts_config).resolve()
    logger.debug(f"Checking path '{bind_mounts_config}'")

    if not bind_mounts_config.exists():
        # No path, so we return zero. This is a common case, so we don't
        # want to exit with an error.
        logger.debug(f"{bind_mounts_config} does not exist.")
        sys.exit(0)

    # Import the YAML
    with open(bind_mounts_config, "rb") as f:
        configuration = yaml.safe_load(f)

    # The format for the YAML is a list of dictionaries, each with a 'source',
    # 'destination' and an optional 'options' key, which is a list of strings.
    # Example:
    # - source: $HOME/.config/rhel-developer-toolbox/per_container/12345/resolv.conf
    #   destination: /etc/resolv.conf
    #   options:
    #     - ro
    # - source: $HOME/.config/rhel-developer-toolbox/per_container/12345/hosts
    #   destination: /etc/hosts
    for bind_mount in configuration:
        # Make sure the source and destination keys are present and that the
        # paths are valid.
        if "source" not in bind_mount or "destination" not in bind_mount:
            logger.error(f"Source or destination not found in {bind_mount}")
            continue
        if not Path(bind_mount["source"]).exists():
            logger.error(f"Source {bind_mount['source']} not found")
            continue

        # If the destination doesn't exist, we create it.
        if not Path(bind_mount["destination"]).exists():
            # If the source is a file, create an empty file at the destination.
            if Path(bind_mount["source"]).is_file():
                Path(bind_mount["destination"]).touch()

            # If the source is a directory, create it.
            elif Path(bind_mount["source"]).is_dir():
                os.makedirs(bind_mount["destination"], exist_ok=True)
            else:
                logger.error(
                    f"Source {bind_mount['source']} is not a file or directory"
                )
                continue

        if Path(bind_mount["source"]).is_file():
            # Bind mount the file
            try:
                bind_mount_file(bind_mount["source"], bind_mount["destination"])
            except BindMountError as e:
                logger.error(
                    f"Error binding {bind_mount['source']} to {bind_mount['destination']}: {e}"
                )
                continue
            except FileNotFoundError as e:
                logger.exception(e)
                continue


if __name__ == "__main__":
    main()
