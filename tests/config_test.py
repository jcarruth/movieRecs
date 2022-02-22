""" Tests for app configuration capabilities """
import os.path
import tempfile
import unittest

from movie_recs import create_app


class ConfigTest(unittest.TestCase):
    """ Tests for app configuration capabilities """

    def test_default_testing_mode(self):
        """ By default, app should be created with testing set to False """
        app = create_app()
        self.assertFalse(app.testing)

    def test_testing_mode_argument(self):
        """ App test mode should be settable through config argument """

        for testing_enabled in (False, True):
            with self.subTest(testing_enabled=testing_enabled):
                app = create_app({"TESTING": testing_enabled})
                self.assertEqual(app.testing, testing_enabled)

    def test_testing_mode_config_file(self):
        """ App test mode should be settable through config file in instance path """

        for testing_enabled in (False, True):
            with tempfile.TemporaryDirectory() as temp_instance_dir:
                temp_config_path = os.path.join(temp_instance_dir, "config.py")
                with open(temp_config_path, mode='w', encoding="utf-8") as temp_config_file:
                    temp_config_file.write(f"TESTING = {testing_enabled}")

                with self.subTest(testing_enabled=testing_enabled):
                    app = create_app(instance_path=temp_instance_dir)
                    self.assertEqual(app.testing, testing_enabled)
