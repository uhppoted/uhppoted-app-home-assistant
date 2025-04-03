'''
UHPPOTED lookup functions unit tests.

Tests the lookup for decorated events.
'''

import unittest

from custom_components.uhppoted import config

OPTIONS = {
    'cards': [{
        'card_name': 'Harry',
        'card_number': 10058400,
        'card_unique_id': '061aeb5d-ea7f-462b-9af2-2d0e0bd8a676'
    }, {
        'card_name': 'Hermione',
        'card_number': 10058401,
        'card_unique_id': 'b868c221-7580-4d39-b7b0-ce9c36d13e13'
    }],
    'controllers': [{
        'controller_address': '192.168.1.100',
        'controller_id': 'Alpha',
        'controller_port': 60000,
        'controller_protocol': 'UDP',
        'controller_serial_number': '405419896',
        'controller_timezone': 'UTC',
        'controller_unique_id': '3b9163ff-2f9d-454f-8462-e7c49a539be0'
    }, {
        'controller_address': '192.168.1.100',
        'controller_id': 'Beta',
        'controller_port': 60000,
        'controller_protocol': 'UDP',
        'controller_serial_number': '303986753',
        'controller_timezone': 'UTC',
        'controller_unique_id': 'e3605792-c229-4b0c-b387-1e32c3365c1a'
    }],
    'doors': [{
        'door_controller': 'Alpha',
        'door_id': 'Gryffindor',
        'door_number': 1,
        'door_unique_id': '5913ccdf-bd94-49ed-af66-56391cb8e4a8'
    }, {
        'door_controller': 'Alpha',
        'door_id': 'Hufflepuff',
        'door_number': 2,
        'door_unique_id': 'eecb5e91-40e8-4950-8b4b-f51f4b401427'
    }, {
        'door_controller': 'Alpha',
        'door_id': 'Ravenclaw',
        'door_number': 3,
        'door_unique_id': '98a5f197-743b-47d8-9afd-f937235c9f54'
    }, {
        'door_controller': 'Alpha',
        'door_id': 'Slytherin',
        'door_number': 4,
        'door_unique_id': '8949b954-239f-4c5d-ba21-9ea7f50db1d9'
    }, {
        'door_controller': 'Beta',
        'door_id': 'Great Hall',
        'door_number': 1,
        'door_unique_id': '74654e92-0d7a-45a1-88b6-160a13c69e92'
    }, {
        'door_controller': 'Beta',
        'door_id': 'Dungeon',
        'door_number': 2,
        'door_unique_id': '6ccfcb14-345d-4ed7-823d-b950bf5d8f98'
    }, {
        'door_controller': 'Beta',
        'door_id': 'Kitchen',
        'door_number': 3,
        'door_unique_id': '69f9cdb3-6393-47bd-98bc-0748a8ace39f'
    }],
}


class TestDecoratedEventLookup(unittest.TestCase):

    def test_lookup_door(self):
        '''
        Tests lookup_door function for multiple controller + door combinations.
        '''
        # yapf: disable
        tests = [
            { 'door': '405419896.1', 'expected': 'Gryffindor' },
            { 'door': '405419896.2', 'expected': 'Hufflepuff' },
            { 'door': '405419896.3', 'expected': 'Ravenclaw'  },
            { 'door': '405419896.4', 'expected': 'Slytherin'  },
            { 'door': '303986753.1', 'expected': 'Great Hall' },
            { 'door': '303986753.2', 'expected': 'Dungeon'    },
            { 'door': '303986753.3', 'expected': 'Kitchen'    },
            { 'door': '303986753.4', 'expected': '(unknown)'  },
        ]
        # yapf: enable

        for test in tests:
            self.assertEqual(config.lookup_door(OPTIONS, test['door']), test['expected'])


if __name__ == '__main__':
    unittest.main()
