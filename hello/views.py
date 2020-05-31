from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Friend
from .forms import FriendForm
from .forms import FindForm
from .forms import CheckForm

def index(request):
    data = Friend.objects.all().order_by('age')
    params = {
            'title': 'Hello',
            'message': '',
            'data': data,
        }
    return render(request, 'hello/index.html', params)


def create(request):
    if (request.method == 'POST'):
        obj = Friend()
        friend = FriendForm(request.POST, instance=obj)
        friend.save()
        return redirect(to = '/hello')
    params = {
            'title': 'Create',
            'form': FriendForm()
    }
    return render(request, 'hello/create.html', params)


def edit(request, num):
    obj = Friend.objects.get(id=num)
    if(request.method == 'POST'):
        friend = FriendForm(request.POST, instance=obj)
        friend.save()
        return redirect(to='/hello')
    params = {
            'title': 'Edit',
            'id': num,
            'form': FriendForm(instance=obj),
    }
    return render(request, 'hello/edit.html', params)


def delete(request, num):
    friend = Friend.objects.get(id=num)
    if(request.method == 'POST'):
        friend.delete()
        return redirect(to='/hello')
    params = {
            'title': 'Delete',
            'id': num,
            'obj': friend,
    }
    return render(request, 'hello/delete.html', params)

def find(request):
    if(request.method == 'POST'):
        msg = 'search result :'
        form = FindForm(request.POST)
        str = request.POST['find']
        list = str.split()
        data = Friend.objects.all()[int(list[0]):int(list[1])]
    else:
        msg = 'search words ...'
        form = FindForm()
        data = Friend.objects.all()
    params = {
            'title': 'Find',
            'message': msg,
            'form': form,
            'data': data,
        }
    return render(request, 'hello/find.html', params)

def check(request):
    params = {
            'title': 'Check',
            'message':'check validation.',
            'form': CheckForm(),
    }
    if (request.method == 'POST'):
        form = CheckForm(request.POST)
        params['form'] = form
        if (form.is_valid()):
            params['message'] = 'OK'
        else:
            params['message'] = 'Not good...'
    return render(request, 'hello/check.html', params)
