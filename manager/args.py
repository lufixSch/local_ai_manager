import os
from argparse import ArgumentParser, Namespace


def default(parser: ArgumentParser):
    """
    Add arguments which are needed by all managers
    """

    parser.add_argument(
        "--automatic1111-location",
        help="Location of AUTOMATIC1111/stable-diffusion-webui | AUTOMATIC1111_LOCATION",
        type=str,
        default=os.environ.get("AUTOMATIC1111_LOCATION"),
    )
    parser.add_argument(
        "--automatic1111-venv",
        help="Location of AUTOMATIC1111/stable-diffusion-webui virtual environment | AUTOMATIC1111_VENV",
        type=str,
        default=os.environ.get("AUTOMATIC1111_VENV"),
    )
    parser.add_argument(
        "--oobabooga-location",
        help="Location of oobabooga/text-generation-webui | OOBABOOGA_LOCATION",
        type=str,
        default=os.environ.get("OOBABOOGA_LOCATION"),
    )
    parser.add_argument(
        "--oobabooga-venv",
        help="Location of oobabooga/text-generation-webui virtual environment | OOBABOOGA_VENV",
        type=str,
        default=os.environ.get("OOBABOOGA_VENV"),
    )


def validate(args: Namespace) -> dict[str, bool]:
    """
    Validate arguments for all managers
    """

    enabled_tools = {"automatic1111": False, "oobabooga": False}

    if not args.automatic1111_location or not args.automatic1111_venv:
        print("AUTOMATIC1111 disabled - Missing location or venv")
        enabled_tools["automatic1111"] = False
    elif not os.path.exists(os.path.join(args.automatic1111_location, "webui.sh")):
        print(
            f"Invalid AUTOMATIC1111 location - {os.path.join(args.automatic1111_location, 'webui.sh')}"
        )
        exit(1)
    elif not os.path.exists(os.path.join(args.automatic1111_venv, "bin", "activate")):
        print("Invalid AUTOMATIC1111 venv - Missing location or unsupported")
        exit(1)
    else:
        enabled_tools["automatic1111"] = True

    if not args.oobabooga_location or not args.oobabooga_venv:
        print("OOBABOGA disabled - Missing location or venv")
        enabled_tools["oobabooga"] = False
    elif not os.path.exists(os.path.join(args.oobabooga_location, "webui.sh")):
        print(
            f"Invalid OOBABOGA location - {os.path.join(args.oobabooga_location, 'webui.sh')}"
        )
        exit(1)
    elif not os.path.exists(os.path.join(args.oobabooga_venv, "bin", "activate")):
        print("Invalid OOBABOGA venv - Missing location or unsupported")
        exit(1)
    else:
        enabled_tools["oobabooga"] = True

    return enabled_tools
