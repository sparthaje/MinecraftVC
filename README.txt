This tool allows one to manage Minecraft backups in an online/offline fashion using Dropbox as a backend. Similar to Minecraft's own command line, MinecraftVC uses its own form of a command system. 

NOTE: COMMAND WITH DESCRIPTIONS STARTING WITH !!! WILL REPLACE FILES

Settings:

/settings view
	shows the user to view what settings the tool is using
/settings edits
	opens settings.txt, so that the user can edit it

Local Backups:

/backup view
	writes newest backup to the console
/backup branch_name
	backs up all the worlds in /saves to the backup_directory/branch_name/new_backup
/backup branch_name symbol
	backs up all the worlds in /saves to the backup_directory/branch_name/new_backup that starts with symbol
/backup retrieve branch_name backup_name
	!!! retrieves all worlds in /backup_directory/branch_name/backup_name/ into /saves
/backup dropbox
	backs up all worlds in /MinecraftVC in dropbox to backup_directory/dropbox

Online Backups:

/push
	!!! Uploads all worlds in /saves to /MinecraftVC/main folder in dropbox
		Will only upload worlds starting with "*" (can be changed in settings)
/push branch_name
	!!! Uploads all worlds in /saves to /MinecraftVC/branch_name folder in dropbox
		Will only upload worlds starting with "*" (can be changed in settings)
/push branch_name symbol
	!!! Uploads all worlds in /saves to /MinecraftVC/branch_name folder in dropbox
		starting with symbol
/push branch_name all
	!!! Uploads all worlds in /saves to /MinecraftVC/branch_name folder in dropbox
/pull
	!!! Replaces all words in /saves with worlds im /MinecraftVC/main
	Only pulls worlds starting with "*" (can be changed in settings)
/pull branch_name
	!!! Replaces all worlds in /saves with worlds in /MinecraftVC/branch_name
	Only pulls worlds starting with "*" (can be changed in settings)
/pull branch_name symbol
	!!! Replaces all worlds in /saves with worlds in /MinecraftVC/branch_name
	Only pulls wolrds starting with symbol
/pull branch_name all
	!!! Replaces all worlds in /saves with worlds in /MinecraftVC/branch_name


Other:

/help
	Lists all the commands avaliable to the console
/clear
	Clears the console
/quit
	Closes the application
