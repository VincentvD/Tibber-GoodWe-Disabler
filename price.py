import os
import tibber.const
import tibber
import asyncio

async def get_price():
  api_token = os.getenv("TIBBER_API_TOKEN", "")
  tibber_connection = tibber.Tibber(api_token, user_agent="GoodweScript")
  await tibber_connection.update_info()

  home = tibber_connection.get_homes()[0]

  await home.fetch_consumption_data()
  await home.update_info()
  await home.update_price_info()

  print(tibber_connection.name + " (" + home.address1 + ")")
  print(home.current_price_info)

  await tibber_connection.close_connection()

  return home.current_price_info

if __name__ == "__main__":
    asyncio.run(get_price())