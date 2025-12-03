from wxgtd.model.db import connect
from wxgtd.model.objects import Folder

Session = connect(r'C:\Users\Johan\.local\share\wxgtd\wxgtd.db')
session = Session()
folders = session.query(Folder).all()
print(f'Folders in database: {len(folders)}')
for f in folders:
    print(f'  - UUID: {f.uuid} | Title: {f.title} | Visible: {f.visible}')

