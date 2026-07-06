#!/usr/bin/python3

import click
import logging
import sys
import yaml

from pathlib import Path


logger = logging.getLogger(__name__)


default_localvars = (
    Path.home() / ".config" / "rhel-developer-toolbox" / "ansible" / "localvars.yaml"
)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    show_default=True,
)
@click.option("--localvarspath", type=click.Path(), default=default_localvars)
@click.argument("operator", type=click.Choice(['autoconfigure', 'rdtx_edit_config_git_managed']))
def main(log_level, operator, localvarspath):
    logging.basicConfig(
        format="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
        level=log_level,
    )
    logger.debug("Debug logging enabled")

    localvarspath = Path(localvarspath).resolve()
    logger.debug(f"Checking path '{localvarspath}'")

    if not localvarspath.exists():
        # No path, so we return non-zero to avoid running the playbook
        logger.debug(f"{localvarspath} does not exist.")
        sys.exit(1)

    # Import the YAML and check for the autoconfiguration setting
    with open(localvarspath, "rb") as f:
        configuration = yaml.safe_load(f)

    if not configuration:
        logger.debug("Empty config file?")
        sys.exit(1)

    if operator == 'autoconfigure':
        # Check for the "autoconfigure" option, defaulting to False if it's
        # not found
        if configuration.get("autoconfigure", False):
            logger.debug("Autoconfiguration is enabled")
            sys.exit(0)

    if operator == 'rdtx_edit_config_git_managed':
        if configuration.get("rdtx_edit_config_git_managed", False):
            logger.debug("rdtx-edit-config git mgmt enabled")
            sys.exit(0)

    logger.debug(f"Option is not enabled: {operator}")
    sys.exit(1)


if __name__ == "__main__":
    main()
