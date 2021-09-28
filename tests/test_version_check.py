import unittest
from unittest.mock import Mock, patch

from tests.helpers.builders import PyPiProjectInfoBuilder, ReleaseInfoBuilder
from tests.helpers.utils import AnyStringWith
from torque.services.version import VersionCheckService


class VersionCheckServiceTests(unittest.TestCase):
    @patch("torque.services.version.requests")
    def test_no_newer_version_in_info(self, requests_mock):
        # arrange
        versions_checker = VersionCheckService("1.0.0")
        versions_checker._show_new_version_message = Mock()
        project_info = PyPiProjectInfoBuilder().with_version("1.0.0").build()
        requests_mock.get.return_value = Mock(json=Mock(return_value=project_info))

        # act
        versions_checker.check_for_new_version_safely()

        # assert
        versions_checker._show_new_version_message.assert_not_called()

    @patch("torque.services.version.requests")
    def test_newer_version_detected_in_info(self, requests_mock):
        # arrange
        versions_checker = VersionCheckService("1.0.0")
        versions_checker._show_new_version_message = Mock()
        project_info = PyPiProjectInfoBuilder().with_version("1.1.0").build()
        requests_mock.get.return_value = Mock(json=Mock(return_value=project_info))

        # act
        versions_checker.check_for_new_version_safely()

        # assert
        versions_checker._show_new_version_message.assert_called_once()

    @patch("torque.services.version.requests")
    def test_newer_version_detected_in_releases(self, requests_mock):
        # arrange
        versions_checker = VersionCheckService("1.0.0")
        versions_checker._show_new_version_message = Mock()
        versions_checker._find_latest_release = Mock(return_value="1.2.0")
        project_info = PyPiProjectInfoBuilder().with_version("1.1.0b1").build()  # project info is pre-release
        requests_mock.get.return_value = Mock(json=Mock(return_value=project_info))

        # act
        versions_checker.check_for_new_version_safely()

        # assert
        versions_checker._find_latest_release.assert_called_once()
        versions_checker._show_new_version_message.assert_called_once()

    @patch("torque.services.version.requests")
    def test_prerelease_in_info_and_no_new_version_in_releases(self, requests_mock):
        # arrange
        versions_checker = VersionCheckService("1.0.0")
        versions_checker._show_new_version_message = Mock()
        versions_checker._find_latest_release = Mock(return_value="1.0.0")
        project_info = PyPiProjectInfoBuilder().with_version("1.1.0b1").build()  # project info is pre-release
        requests_mock.get.return_value = Mock(json=Mock(return_value=project_info))

        # act
        versions_checker.check_for_new_version_safely()

        # assert
        versions_checker._find_latest_release.assert_called_once()
        versions_checker._show_new_version_message.assert_not_called()

    def test_find_latest_release(self):
        # arrange
        versions_checker = VersionCheckService("1.0.0")

        project_info = (
            PyPiProjectInfoBuilder()
            .with_version("1.1.0b1")
            .with_release(ReleaseInfoBuilder("1.2.0b1").with_yanked(True))
            .with_release(ReleaseInfoBuilder("1.1.0b1"))
            .with_release(ReleaseInfoBuilder("1.0.1"))
            .with_release(ReleaseInfoBuilder("1.0.0"))
            .build()
        )

        # act
        latest_version = versions_checker._find_latest_release(project_info)

        # assert
        self.assertEqual("1.0.1", latest_version)

    # @patch("torque.services.version.BaseCommand")
    # def test_show_new_version_message(self, base_command_mock):
    #     # arrange
    #     versions_checker = VersionCheckService("1.0.0")
    #     latest_version = Mock()
    #
    #     # act
    #     versions_checker._show_new_version_message(latest_version)
    #
    #     # assert
    #     base_command_mock.message.assert_called_once_with(AnyStringWith(latest_version))

    @patch("torque.services.version.requests")
    def test_check_for_new_version_is_safe(self, requests_mock):
        # arrange 1
        versions_checker = VersionCheckService("1.0.0")
        versions_checker._show_new_version_message = Mock()
        requests_mock.get = Mock(side_effect=Exception())

        # act 1
        versions_checker.check_for_new_version_safely()
        versions_checker._show_new_version_message.assert_not_called()

        # arrange 2
        project_info = PyPiProjectInfoBuilder().with_version("BAD_VERSION").build()
        requests_mock.get.side_effect = None
        requests_mock.get.return_value = Mock(json=Mock(return_value=project_info))
        versions_checker._find_latest_release = Mock(side_effect=Exception())

        # act 2
        versions_checker.check_for_new_version_safely()
