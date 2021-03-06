from django.shortcuts import render
from django.http import JsonResponse
import os

# Create your views here.
def toupload(request):
    pass
    return render(request, 'upload/upload.html')

# 检查上传分片是否重复，如果重复则不提交，否则提交
def checkChunk(request):
    # post请求
    if request.method == 'POST':
        # 获得上传文件块的大小,如果为0，就告诉他不要上传了
        chunkSize = request.POST.get("chunkSize")
        if chunkSize == '0':
            return JsonResponse({'ifExist': True})
        # 如果文件块大小不为0 ，那么就上传，需要拼接一个临时文件
        file_name = request.POST.get('fileMd5')+request.POST.get('chunk')

        # 如果说这个文件不在已经上传的目录，就可以上传，已经存在了就不需要上传。
        if file_name not in get_deep_data():
            return JsonResponse({'ifExist': False})
        return JsonResponse({'ifExist': True})

# 判断一个文件是否在一个目录下
def get_deep_data(path='user/upload/'):
    result = []
    data = os.listdir(path)
    for i in data:
        if os.path.isdir(i):
            get_deep_data(i)
        else:
            result.append(i)
    return result


# 前端上传的分片 保存到 指定的目录下
def upload(request):
    if request.method == 'POST':
        md5 = request.POST.get("fileMd5")
        chunk_id = request.POST.get("chunk","0")
        fileName = "%s-%s"%(md5,chunk_id)
        file = request.FILES.get("file")
        with open('user/upload/'+fileName,'wb') as f:
            for i in file.chunks():
                f.write(i)
        return JsonResponse({'upload_part':True})


# 将每次上传的分片合并成一个新文件
def mergeChunks(request):
    if request.method == 'POST':
        # 获取需要给文件命名的名称
        fileName = request.POST.get("fileName")
        # 该图片上传使用的md5码值
        md5 = request.POST.get("fileMd5")
        id = request.POST.get("fileId")
        # 分片的序号
        chunk = 0
        # 完成的文件的地址为
        path = os.path.join('user','upload',fileName)
        with open(path,'wb') as fp:
            while True:
                try:
                    filename = 'user/upload/{}-{}'.format(md5,chunk)
                    with open(filename,'rb') as f:
                        fp.write(f.read())
                    # 当图片写入完成后，分片就没有意义了，删除
                    os.remove(filename)
                except:
                    break
                chunk += 1

        return JsonResponse({'upload':True,'fileName':fileName,'fileId':id})