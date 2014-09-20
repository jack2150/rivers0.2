# usage classes
from glob import glob

# system variables
from rivers.settings import FILES


class OpenDir(object):
    def __init__(self):
        self.folder = FILES['position_statement']

        self.files = []
        self.json = ''

    def get_files_from_folder(self):
        """
        Open positions folder and
        get all files inside folder
        Return a file list
        :rtype : list
        """
        return glob(self.folder + '/*.csv')

    @classmethod
    def get_date_from_fpath(cls, path):
        """
        Return date from file path
        :rtype : str
        """
        return path.split('\\')[-1][:10]

    @classmethod
    def make_dict(cls, path):
        """
        Using file name create a dict that
        include 'Date' and 'Path'
        :rtype : dict
        """
        return dict(Date=OpenDir.get_date_from_fpath(path), Path=path)

    def to_list(self):
        """
        Return positions files dict
        :rtype : list of dict
        """
        if not len(self.files):
            fpaths = self.get_files_from_folder()

            for fpath in fpaths:
                self.files.append(OpenDir.make_dict(fpath))

        return self.files

    @classmethod
    def get_fname_from_path(cls, path):
        """
        From file path return file name
        :rtype : str
        """
        return path.split('\\')[-1]

    def to_json(self):
        """
        Return json format variables
        :rtype : str
        """
        if not self.json:
            fpaths = self.get_files_from_folder()

            for fpath in fpaths:
                self.json += '{"id": "%s", "value": "%s"},' \
                             % (OpenDir.get_date_from_fpath(fpath),
                                OpenDir.get_fname_from_path(fpath))
            self.json = '[' + self.json[:-1] + ']'

        return self.json

    def get_path(self, date):
        """
        Get the path using date
        :param date: str
        :return: str
        """
        paths = self.get_files_from_folder()

        result = ''
        for path in paths:
            if date in path:
                result = path

        return result