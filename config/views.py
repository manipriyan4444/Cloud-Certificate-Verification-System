from django.shortcuts import render

def custom_bad_request(request, exception=None):
    return render(request, '400.html', status=400)

def custom_permission_denied(request, exception=None):
    return render(request, '403.html', status=403)

def custom_page_not_found(request, exception=None):
    return render(request, '404.html', status=404)

def custom_server_error(request):
    return render(request, '500.html', status=500)
