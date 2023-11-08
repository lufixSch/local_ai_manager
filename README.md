# Local AI Manager

Allows you to run/monitor local AI tools like oobabooga/text-generation-webui with a service in the background.

**Supported Tools**
- [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui)
- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

**Supported Manager**
- MQTT

## Usage

Each manager can be started using the according python script in project root. The manager can then be configured using command line arguments. Use `--help` to get a detailed information about the available attributes.

> Each configuration can also be defined using an environment variable. The required name is also given with the `--help` command

### Run in background

For linux devices there is a service for each manager in `services/`. Just fill in the missing bits like the *user* and the *path* to the `*_manager.py` and copy it into your systemd folder `/etc/systemd/**`.

The startup options for the manager are loaded as environment variables from a config file by the systemd service. An example is provided in `services/`. Copy this file to the location defined in the systemd file (`/etc/local_ai_manager/*.conf`) and set the variables according to your setup.

> As this file might include secrets, make sure to set the permissions so that only user with admin rights can read (and edit) this file.

Now you can start the service and enable it to autostart.

```bash
systemctl daemon-reload
systemctl start *_ai_manager
systemctl enable *_ai_manager
```

Check the status of your service with `systemctl status *_ai_manager`

## Standalone systemd services

This repository also features some standalone systemd services which can be used to run the given tool in the background.

**Supported Tools**
- [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui)
- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)