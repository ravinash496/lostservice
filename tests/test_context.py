#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import lostservice.context as context


class ContextTest(unittest.TestCase):

    def test_load_from_passed_file(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        target = context.LostContext(config_file=custom_ini_file)
        expected = 'postgresql://squidward:sandy@spongebob:1111/patrick'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)

    def test_load_from_env_file(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        os.environ[context._CONFIGFILE] = custom_ini_file
        target = context.LostContext()
        expected = 'postgresql://squidward:sandy@spongebob:1111/patrick'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)
        os.environ.pop(context._CONFIGFILE)

    def test_load_from_env_values(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        os.environ[context._CONFIGFILE] = custom_ini_file
        os.environ[context._DBHOSTNAME] = 'DBHOSTNAME'
        os.environ[context._DBPORT] = 'DBPORT'
        os.environ[context._DBNAME] = 'DBNAME'
        os.environ[context._DBUSER] = 'DBUSER'
        os.environ[context._DBPASSWORD] = 'DBPASSWORD'

        target = context.LostContext()
        expected = 'postgresql://DBUSER:DBPASSWORD@DBHOSTNAME:DBPORT/DBNAME'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)

        os.environ.pop(context._CONFIGFILE)
        os.environ.pop(context._DBHOSTNAME)
        os.environ.pop(context._DBPORT)
        os.environ.pop(context._DBNAME)
        os.environ.pop(context._DBUSER)
        os.environ.pop(context._DBPASSWORD)

    def test_load_fail(self):
        with self.assertRaises(context.ContextException):
            target = context.LostContext()


if __name__ == '__main__':
    unittest.main()