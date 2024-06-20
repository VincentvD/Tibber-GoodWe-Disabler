import datetime
import os
import asyncio
import goodwe
import schedule
import price

global_vars = {
    "gridExportIsEnabled": False,
}

async def get_runtime_data() -> None:
    inverter_ip_address = os.getenv("INVERTER_IP_ADDRESS", "")
    inverter = await goodwe.connect(inverter_ip_address)

    runtime_data = await inverter.read_runtime_data()

    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            print(f"{sensor.id_}: \t\t {sensor.name} = {runtime_data[sensor.id_]} {sensor.unit}")


async def get_settings_data() -> None:
    inverter_ip_address = os.getenv("INVERTER_IP_ADDRESS", "")
    inverter = await goodwe.connect(inverter_ip_address)

    settings_data = await inverter.read_settings_data()

    for setting in inverter.settings():
        if setting.id_ in settings_data:
            print(f"{setting.id_}: \t\t {setting.name} = {settings_data[setting.id_]} {setting.unit}")

async def setInverterGridExport(shutdownInverter: bool) -> None:
    inverter_ip_address = os.getenv("INVERTER_IP_ADDRESS", "")
    inverter = await goodwe.connect(inverter_ip_address)

    if(global_vars["gridExportIsEnabled"] == False):
        gridExport: int = await inverter.read_setting("grid_export")
        if(gridExport == 0):
            await inverter.write_setting("grid_export", 1)
        global_vars["gridExportIsEnabled"] = True

    gridExportLimit: int = await inverter.read_setting("grid_export_limit")

    if(shutdownInverter):
        if(gridExportLimit > 0):
            await inverter.write_setting("grid_export_limit", 0)
            print("DISABLING INVERTER ")
    else:
        if(gridExportLimit != 100):
            await inverter.write_setting("grid_export_limit", 100)
            print("ENABLING INVERTER ") 

async def job() -> None:
    price_threshold = float(os.getenv("PRICE_THRESHOLD", -0.10))
    price_data = await price.get_price()
    total_price = price_data['total']
    print(f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Current kWh price: {total_price} EUR")
    if(total_price < price_threshold):
        await setInverterGridExport(True)
    else:
        await setInverterGridExport(False)

def run_job() -> None:
    asyncio.create_task(job())

async def main() -> None:
    # Run the job immediately on startup
    await job()
    
    # Schedule the job to run every 5 minutes
    schedule.every(5).minutes.do(run_job)
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Create a new event loop if there is no current event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())