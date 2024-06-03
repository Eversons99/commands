from files_manager_app.utils.files_service import FilesUtility
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'homepageFiles.html')


def get_files(request):
    if request.method == 'GET':
        files_information = FilesUtility.get_files_info(request)
        files_formatted = FilesUtility.format_files_to_render(files_information)

        context = {
            'files': files_formatted,
            'filtered': True,
            'selected_filter': files_information.get('selected_filter'),
            'warn_message': 'A pesquisa não retornou nenhum arquivo' if files_information.get('number_of_files') == 0 else ''    
        }

        return render(request, 'homepageFiles.html', context)

    return redirect(home)


def show_logs(request):
    if request.method == 'GET':
        maintenance_info = FilesUtility.get_logs_info(request)

        context = {
            'model_title': maintenance_info.get('model_title'),
            'name': maintenance_info.get('general_info').file_name,
            'logs': maintenance_info.get('general_info').logs,
            'rollback_logs': maintenance_info.get('general_info').rollback_logs,
            'last_filter_url': maintenance_info.get('last_filter_url')
        }

        return render(request, 'fileLogs.html', context)
        
    return redirect(home)
