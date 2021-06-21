import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Folder, File


@csrf_exempt
def make_folder(request):
    if 'id' not in request.POST:
        parent_folder = None
    else:
        parent_folder = Folder.objects.get(id=request.POST['id'])

    try:
        new_folder = {'name': request.POST['name']}
    except KeyError:
        return HttpResponse("Key Error")

    for folder in Folder.objects.filter(name=new_folder['name']):
        if folder.parent == parent_folder:
            return HttpResponse("A folder with the same name exists")

    new_folder_object = Folder.objects.create(name=new_folder['name'], parent=parent_folder)
    return HttpResponse(json.dumps({"id": str(new_folder_object.id)}))


@csrf_exempt
def search_folder(request):
    try:
        folder_id = request.POST['id']
    except KeyError:
        return HttpResponse("Key Error")
    parent_folder = Folder.objects.get(id=folder_id)
    if parent_folder is not None:
        child_folder = Folder.objects.filter(parent_id=folder_id)
        child_file = File.objects.filter(parent_id=folder_id)
        child_list = {'folder_count': child_folder.count(), 'folder': [],
                      'file_count': child_file.count(), 'file': []}

        for folder in child_folder:
            folder_data = {'name': folder.name}
            child_list['folder'].append(folder_data)

        for file in child_file:
            file_data = {'id': file.id, 'title': file.title, 'size': 0}
            if file.contents:
                file_data['size'] = file.contents.size

            child_list['file'].append(file_data)

        return HttpResponse(json.dumps(child_list, ensure_ascii=False))
    else:
        return HttpResponse("Folder Not Found")


@csrf_exempt
def make_file(request):
    try:
        parent_folder = Folder.objects.get(id=request.POST['id'])
        new_file = {'title': request.POST['title']}
    except KeyError:
        return HttpResponse("Key Error")

    for file in File.objects.filter(title=new_file['title']):
        if file.parent == parent_folder:
            return HttpResponse("A file with the same name exists")

    new_file_object = File.objects.create(title=new_file['title'], parent=parent_folder)
    return HttpResponse(json.dumps({"id": str(new_file_object.id)}))


@csrf_exempt
def search_file(request):
    try:
        file_object = File.objects.get(id=request.POST['id'])
        if file_object is None:
            return HttpResponse("File not Found")
    except KeyError:
        return HttpResponse("Key Error")

    file_data = {'title': file_object.title, 'size': 0, 'contents': ""}
    if file_object.contents:
        file_data['size'] = file_object.contents.size
        file_data['contents'] = file_object.contents.read().decode('utf-8')

    return HttpResponse(json.dumps(file_data, ensure_ascii=False))


@csrf_exempt
def update_file(request):
    try:
        file_object = File.objects.get(id=request.POST['id'])

        if file_object is None:
            return HttpResponse("File not Found")

        file_object.contents = request.FILES['contents']
        file_object.save(update_fields=['contents'])
    except KeyError:
        return HttpResponse("Key Error")

    return HttpResponse(file_object.contents.read())
