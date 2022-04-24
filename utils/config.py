import sys
from dotenv import dotenv_values


def get_config():
    """Get the configuration for the bot"""

    # Set bot runmode (DEV | PROD)
    runmode = "PROD"

    # Load configuration from config file
    if runmode == "DEV":
        config = dotenv_values(".dev.env")
    elif runmode == "PROD":
        config = dotenv_values(".prod.env")
    else:
        print("Please specify runmode")
        sys.exit(-1)

    return config
