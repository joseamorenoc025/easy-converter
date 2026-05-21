from PyInstaller.utils.hooks import collect_data_files

# Recopilar los archivos de datos necesarios para tkinterdnd2 (específicamente la carpeta tkdnd)
datas = collect_data_files('tkinterdnd2')
