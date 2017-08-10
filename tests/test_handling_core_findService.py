#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.handling.core
import lostservice.model.requests
import lostservice.model.location


class FindServiceTest(unittest.TestCase):

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    @patch('lostservice.db.utilities.apply_policy_settings')
    def test_handle_point(self, mockconfig, mockdb, apply_policy_settings):

        '''
        # Mock for apply_policy_settings.
        apply_policy_settings = MagicMock()
        apply_policy_settings.return_value = []

        # Mock for config.
        mockconfig.get = MagicMock()


        # Mocks for db.
        mockdb.get_urn_table_mappings = MagicMock()
        mockdb.get_urn_table_mappings.return_value = {'foo': 'bar'}

        mockdb.get_containing_boundary_for_point = MagicMock()
        mockdb.get_containing_boundary_for_point.return_value = [
            {
                'displayname': 'displayname',
                'serviceurn': 'serviceurn',
                'routeuri': 'routeuri',
                'servicenum': 'servicenum'
                'mapping_sourceid': 'mapping_sourceid'
            }
        ]

        target = lostservice.handling.core.FindServiceHandler(mockconfig, mockdb)

        model = lostservice.model.requests.FindServiceRequest()
        location = lostservice.model.location.Point()
        location.longitude = 1.1
        location.latitude = 2.2
        location.spatial_ref = 'foo'

        try:
            target.handle_request(model, {})
        except:
            self.fail("handle_request threw an exception.")
        '''

if __name__ == '__main__':
    unittest.main()
