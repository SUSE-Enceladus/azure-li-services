from unittest.mock import patch

from azure_li_services.users import Users


class TestUsers(object):
    def setup(self):
        self.users = Users()

    @patch('azure_li_services.users.Command.run')
    def test_user_exists(self, mock_command):
        self.users.user_exists('user')
        mock_command.assert_called_once_with(
            ['grep', '-q', '^user:', '/etc/passwd']
        )

    @patch('azure_li_services.users.Command.run')
    def test_user_exists_return_value(self, mock_command):
        assert self.users.user_exists('user') is True
        mock_command.side_effect = Exception
        assert self.users.user_exists('user') is False

    @patch('azure_li_services.users.Command.run')
    def test_group_exists(self, mock_command):
        self.users.group_exists('group')
        mock_command.assert_called_once_with(
            ['grep', '-q', '^group:', '/etc/group']
        )

    @patch('azure_li_services.users.Command.run')
    def test_group_add(self, mock_command):
        self.users.group_add('group', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['groupadd', '--option', 'value', 'group']
        )

    @patch('azure_li_services.users.Command.run')
    def test_user_add(self, mock_command):
        self.users.user_add('user', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['useradd', '--option', 'value', 'user']
        )

    @patch('azure_li_services.users.Command.run')
    def test_user_modify(self, mock_command):
        self.users.user_modify('user', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['usermod', '--option', 'value', 'user']
        )

    @patch('azure_li_services.users.Command.run')
    def test_setup_home_for_user(self, mock_command):
        self.users.setup_home_for_user('user', 'group', '/home/path')
        mock_command.assert_called_once_with(
            ['chown', '-R', 'user:group', '/home/path']
        )

    @patch('azure_li_services.users.Command.run')
    def test_setup_change_password_on_logon(self, mock_command):
        self.users.setup_change_password_on_logon('user')
        mock_command.assert_called_once_with(
            ['chage', '-d', '0', 'user']
        )
