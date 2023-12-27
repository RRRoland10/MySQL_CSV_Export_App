import wx
import wx.grid
import mysql.connector
import csv
from configparser import ConfigParser

class ExportApp(wx.Frame):
    def __init__(self, parent, title):
        super(ExportApp, self).__init__(parent, title=title, size=(800, 600))

        self.panel = wx.Panel(self)
        self.create_widgets()
        self.Centre()
        self.Show()

    def create_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Database Configuration
        hbox_db = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hbox_db, flag=wx.ALL, border=10)

        db_label = wx.StaticText(self.panel, label='Database:')
        hbox_db.Add(db_label, flag=wx.RIGHT, border=8)

        self.db_text = wx.TextCtrl(self.panel)
        hbox_db.Add(self.db_text, proportion=1)

        # Table Configuration
        hbox_table = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hbox_table, flag=wx.ALL, border=10)

        table_label = wx.StaticText(self.panel, label='Table:')
        hbox_table.Add(table_label, flag=wx.RIGHT, border=8)

        self.table_text = wx.TextCtrl(self.panel)
        hbox_table.Add(self.table_text, proportion=1)

        # Export Button
        export_btn = wx.Button(self.panel, label='Export Selected Rows', size=(150, 30))
        export_btn.Bind(wx.EVT_BUTTON, self.export_selected_rows)
        vbox.Add(export_btn, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        # Grid to display data
        self.grid = wx.grid.Grid(self.panel)
        vbox.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.panel.SetSizer(vbox)

    def export_selected_rows(self, event):
        db_name = self.db_text.GetValue()
        table_name = self.table_text.GetValue()

        try:
            db_config = self.read_db_config()
            connection = mysql.connector.connect(**db_config)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(f'SELECT * FROM {table_name}')

            # Get column names
            col_names = cursor.column_names

            # Fetch data
            data = [row for row in cursor]

            # Display data in the grid
            self.grid.CreateGrid(len(data), len(col_names) + 1)  # +1 for the checkbox column
            self.grid.SetColLabelValue(0, 'Select')  # Checkbox column label

            for col, col_name in enumerate(col_names):
                self.grid.SetColLabelValue(col + 1, col_name)  # Shift by 1 to accommodate the checkbox column

            for row, row_data in enumerate(data):
                # Insert checkboxes in the first column
                self.grid.SetCellValue(row, 0, '')
                self.grid.SetCellRenderer(row, 0, wx.grid.GridCellBoolRenderer())
                self.grid.SetCellEditor(row, 0, wx.grid.GridCellBoolEditor())

                for col, col_name in enumerate(col_names):
                    self.grid.SetCellValue(row, col + 1, str(row_data[col_name]))

            wx.MessageBox('Data loaded successfully!', 'Success', wx.OK | wx.ICON_INFORMATION)

        except mysql.connector.Error as err:
            wx.MessageBox(f'Error: {err}', 'Error', wx.OK | wx.ICON_ERROR)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def read_db_config(self, filename='config.ini', section='mysql'):
        parser = ConfigParser()
        parser.read(filename)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(f'Section {section} not found in the {filename} file')

        return db


if __name__ == '__main__':
    app = wx.App()
    ExportApp(None, title='Database Export App')
    app.MainLoop()
