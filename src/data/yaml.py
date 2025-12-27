import yaml
import logging

content = """
---
application_settings:
  database:
    host: localhost
    port: 3306
    name: user_db
  api_keys:
    - d73e6774-5199-47a7-ad32-80e874fda949
"""


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Loaded configuration: %s", data)
