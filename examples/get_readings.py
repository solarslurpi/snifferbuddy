import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from pathlib import Path

    # Get the user's home directory
    home_directory = Path.home()
    # Construct the project directory path
    project_dir = home_directory / "Documents" / "Projects" / "snifferbuddy"

    print(f"Project directory: {project_dir}")
    return Path, home_directory, project_dir


@app.cell

def _():
    import os
    os.listdir()
    return (os,)


@app.cell
def _(project_dir):
    from config import AppConfig
    mqtt_config = AppConfig.from_yaml(project_dir / 'config.yaml')
    mqtt_config
    return AppConfig, mqtt_config


@app.cell
def _(mo, mqtt_config):
    from src.mqtt_code import MQTTListener
    from src.database_code import SensorDatabase

    a = mo.md("# SnifferBuddy Monitor")
    b = mo.md("## Initializing Components")

    database = SensorDatabase(mqtt_config)
    mqtt_client = MQTTListener(mqtt_config, database)

    def on_start_click(event):
        print(f"Starting mqtt....")
        mqtt_client.start()


    start_button = mo.ui.button(on_click=on_start_click, label="Start MQTT")
    mo.vstack([a,b,start_button])
    return (
        MQTTListener,
        SensorDatabase,
        a,
        b,
        database,
        mqtt_client,
        on_start_click,
        start_button,
    )


@app.cell
def _(mqtt_client):
    mqtt_client.stop()
    return


if __name__ == "__main__":
    app.run()
