import copy
import voluptuous as vol

from .const import CONF_CONTROLLERS
# from .const import CONF_CONTROLLER_UNIQUE_ID
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_CONTROLLER_PORT
from .const import CONF_CONTROLLER_TIMEZONE

from .const import DEFAULT_CONTROLLER_ID
from .const import DEFAULT_CONTROLLER_ADDR

class UhppotedFlow:

    def __init__(self):
        pass

    def step_controller(self, controller, options, user_input, default_values):
        serial_no = controller['serial_no']
        address = controller.get('address', DEFAULT_CONTROLLER_ADDR)
        port = controller.get('port', 60000)

        #     errors: Dict[str, str] = {}
        #
        #     if user_input is not None:
        #         name = user_input[CONF_CONTROLLER_ID]
        #         address = user_input[CONF_CONTROLLER_ADDR]
        #         timezone = user_input[CONF_CONTROLLER_TIMEZONE]
        #
        #         try:
        #             validate_controller_id(serial_no, name, None)
        #         except ValueError as err:
        #             errors[CONF_CONTROLLER_ID] = f'{err}'
        #
        #         if not errors:
        #             controllers = self.options[CONF_CONTROLLERS]
        #
        #             for v in self.options[CONF_CONTROLLERS]:
        #                 if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') == int(f'{serial_no}'):
        #                     if user_input[CONF_CONTROLLER_ID].strip() == '-':
        #                         controllers.remove(v)
        #                     else:
        #                         v[CONF_CONTROLLER_ID] = name
        #                         v[CONF_CONTROLLER_ADDR] = address
        #                         v[CONF_CONTROLLER_PORT] = port
        #                         v[CONF_CONTROLLER_TIMEZONE] = timezone
        #                     break
        #             else:
        #                 if user_input[CONF_CONTROLLER_ID].strip() != '-':
        #                     controllers.append({
        #                         CONF_CONTROLLER_UNIQUE_ID: uuid.uuid4(),
        #                         CONF_CONTROLLER_SERIAL_NUMBER: serial_no,
        #                         CONF_CONTROLLER_ID: name,
        #                         CONF_CONTROLLER_ADDR: address,
        #                         CONF_CONTROLLER_PORT: port,
        #                         CONF_CONTROLLER_TIMEZONE: timezone,
        #                     })
        #
        #             self.options.update({CONF_CONTROLLERS: controllers})
        #
        #             controller['configured'] = True
        #
        #             return await self.async_step_controller()

        controller_id = controller.get('name', None)
        if not controller_id or controller_id == '':
            controller_id = controller.get('serial_no', DEFAULT_CONTROLLER_ID)

        defaults = {
            CONF_CONTROLLER_ID: controller_id,
            CONF_CONTROLLER_ADDR: address,
            CONF_CONTROLLER_PORT: port,
            CONF_CONTROLLER_TIMEZONE: default_values[CONF_CONTROLLER_TIMEZONE],  #self._timezone,
        }

        if options != None:
            for v in options.get(CONF_CONTROLLERS, []):
                if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') == int(f'{serial_no}'):
                    for k in [CONF_CONTROLLER_ID, CONF_CONTROLLER_ADDR, CONF_CONTROLLER_TIMEZONE]:
                        if k in v:
                            defaults[k] = v[k]
                    break
        
        if user_input is not None:
            for k in [CONF_CONTROLLER_ID, CONF_CONTROLLER_ADDR, CONF_CONTROLLER_TIMEZONE]:
                if k in user_input:
                    defaults[k] = user_input[k]

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID, default=defaults[CONF_CONTROLLER_ID]): str,
            vol.Optional(CONF_CONTROLLER_ADDR, default=defaults[CONF_CONTROLLER_ADDR]): str,
            vol.Optional(CONF_CONTROLLER_PORT, default=defaults[CONF_CONTROLLER_PORT]): int,
            vol.Optional(CONF_CONTROLLER_TIMEZONE, default=defaults[CONF_CONTROLLER_TIMEZONE]): str,
        })

        placeholders = { 
            "serial_no": serial_no,
        }

        return (schema,placeholders)
