import dropbox
import os

APP_TOKEN ='oR-WfT2o4QAAAAAAAAAACRrcRUoCehRTWkimT6PrXdI7nvVv6LGm85qSJBg9fFN4'

dbx = dropbox.Dropbox(APP_TOKEN)
dbx.users_get_current_account()

for entry in dbx.files_list_folder('').entries:
    print(entry.name)

du = input("Download or Upload (d/u) ")
file = input("file path to download/upload ")
dest = input("file path to destination ")

if (du is "d"):
	with open(dest, "wb") as f:
	    metadata, res = dbx.files_download(path=file)
	    f.write(res.content)
	    f.close()
else:
	with open(file, "rb") as f:
		file_size = os.path.getsize(file)
		CHUNK_SIZE = 4 * 1024 * 1024
		if (file_size < CHUNK_SIZE):
			print(dbx.files_upload(f.read(), dest))