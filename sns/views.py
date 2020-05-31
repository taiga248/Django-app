from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Message, Friend, Group, Good
from .forms import GroupCheckForm, GroupSelectForm, SearchForm, FriendsForm, CreateGroupForm, PostForm

from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
def index(request):
    (public_user, public_group) = get_public()
    if request.method == 'POST':

        if request.POST['mode'] == '__check_form__':
            searchform = SearchForm()
            checkform = GroupCheckForm(request.user, request.POST)
            glist = []
            for item in request.POST.getlist('groups'):
                glist.append(item)
            messages = get_your_group_message(request.user, glist, None)

        if request.POST['mode'] == '__search_form__':
            searchform = SearchForm(request.POST)
            checkform = GroupCheckForm(request.user)
            gps = Group.objects.filter(owner=request.user)
            glist = [public_group]
            for item in gps:
                glist.append(item)
            # メッセージの取得
            messages = get_your_group_message(request.user, glist, request.POST['search'])
    else: 
        searchform = SearchForm()
        checkform = GroupCheckForm(request.user)
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group]
        for item in gps:
            glist.append(item)
        # メッセージの取得
        messages = get_your_group_message(request.user, glist, None)

    # 共通処理
    params = {
            'login_user': request.user,
            'contents': messages,
            'check_form': checkform,
            'search_form': searchform,
        }
    return render(request, 'sns/index.html', params)


@login_required(login_url='/admin/login/')
def groups(request):
    friends = Friend.objects.filter(owner=request.user)
    if request.method == 'POST':
        if request.POST['mode'] == '__groups_form__':
            sel_group = request.POST['groups']
            gp = Group.objects.filter(owner=request.user).filter(title=sel_group).first()
            fds = Friend.objects.filter(owner=request.user).filter(group=gp)
            vlist = []
            for item in fds:
                vlist.append(item.user.username)
            groupsform = GroupSelectForm(request.user, request.POST)
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)

        # フレンドのチェック更新時
        if request.POST['mode'] == '__friends_form__':
            sel_group = request.POST['group']
            group_obj = Group.objects.filter(title=sel_group).first()
            # チェックしたフレンドを取得
            sel_fds = request.POST.getlist('friends')
            # フレンドのユーザーを取得
            sel_users = User.objects.filter(username__in=sel_fds)
            # ユーザーのリストに含まれるユーザーが登録した時のフレンドを取得
            fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
            # 全てのフレンドにグループを設定して保存する
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.username)
            #メッセージを設定
            messages.success(request, 'チェックされたフレンドを' + sel_group + 'に登録しました。')
            # フォームの用意
            groupsform = GroupSelectForm(request.user, { 'groups':sel_group })
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)

    # GETアクセス時の処理
    else:
        # フォームの用意
        groupsform = GroupSelectForm(request.user)
        friendsform = FriendsForm(request.user, friends=friends, vals=[])
        sel_group = '-'

    # 共通処理
    createform = CreateGroupForm()
    params = {
            'login_user': request.user,
            'groups_form': groupsform,
            'friends_form': friendsform,
            'create_form': createform,
            'group': sel_group,
        }
    return render(request, 'sns/groups.html', params)

# フレンドの追加処理
@login_required(login_url='/admin/login/')
def add(request):
    add_name = request.GET['name']
    add_user = User.objects.filter(username=add_name).first()
    # ユーザーが本人だった場合の処理
    if add_user == request.user:
        messages.info(request, "自分自身をフレンドに追加することはできません。")
        return redirect(to='/sns')
    # publicの取得
    (public_user, public_group) = get_public()
    # add_userのフレンドの数を調べる
    frd_num = Friend.objects.filter(owner=request.user).filter(use=add_user).count()
    # ゼロより大きければ既に登録済
    if frd_num > 0:
        messages.info(request, add_user.username + 'は既に追加されています。')
        return redirect(to='/sns')

    # フレンド登録
    frd = Friend()
    frd.owner = request.user 
    frd.user = add_user
    frd.group = public_group
    frd.save() 
    # メッセージ設定
    messages.success(request, add_user.username + 'を追加しました！Groupページに移動して、追加したフレンドをメンバーに設定してください。')
    return redirect(to='/sns')

# グループ作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
    # グループを作り、Userとtitleを設定して保存する
    gp = Group()
    gp.owner = request.user
    gp.title = request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/sns/groups')

# メッセージのポスト
@login_required(login_url='/admin/login/')
def post(request):
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # グループの処理
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # メッセージを作成し設定して保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.save()
        # メッセージを設定
        messages.success(request, '新しいメッセージを投稿しました！')
        return redirect(to='/sns')
    # GETアクセス時の処理
    else:
        form = PostForm(request.user)

    # 共通処理
    params = {
            'login_user': request.user,
            'form': form,
        }
    return render(request, 'sns/post.html', params)

# 投稿をシェアする
@login_required(login_url='/admin/login/')
def share(request, share_id):
    # シェアするメッセージの取得
    share = Message.objects.get(id=share_id)

    # POST送信時の処理　
    if request.method == 'POST':
        # 送信内容を取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # グループの取得
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # メッセージを作成し、設定を保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share.id
        msg.save()
        share_msg = msg.get_share()
        share_msg.share_count += 1
        share_msg.save()
        # メッセージを設定
        messages.seccess(request, 'メッセージをシェアしました！')
        return redirect(to='/sns')

    # 共通処理
    form = PostForm(request.user)
    params = {
            'login_user': request.user,
            'form': form,
            'share': share,
        }
    return render(request, 'sns/share.html', params)

# Goodボタン
@login_required(login_url='/admin/login/')
def good(request, good_id):
    # goodするメッセージを取得
    good_msg = Message.objects.get(id=good_id)
    # 自分がメッセージにGoodした数を調べる
    is_good = Good.objects.filter(owner=request.user).filter(message=good_msg).count()
    # ゼロより大きければ既にGood済
    if is_good > 0:
        messages.success(request, '既にこのメッセージはいいねしています。')
        return redirect(to='/sns')

    # メッセージのいいね数を＋１
    good_msg.good_count += 1
    good_msg.save()
    # Goodを作成し、設定して保存
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()
    # メッセージを設定
    messages.success(request, 'メッセージにいいねしました。')
    return redirect(to='/sns')

# viewに無関係な関数達↓

# 指定されたグループおよび検索文字によるメッセージの取得
def get_your_group_message(owner, glist, find):
    # publicの取得
    (public_user, public_group) = get_public()
    # チェックされたグループの取得
    groups = Group.objects.filter(Q(owner=owner) | Q(owner=public_user)).filter(title__in=glist)
    # グループに含まれるユーザーを取得する
    me_friends = Friend.objects.filter(group__in=groups)
    # フレンドのユーザーをリストにまとめる
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    # ユーザーリストのユーザーが作ったグループ取得
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    if find == None:
        messages = Message.objects.filter(Q(group__in=groups) | Q(group__in=me_groups))[:100]
    else:
        messages = Message.objects.filter(Q(group__in=groups) | Q(group__in=me_groups)).filter(content__contains=find)[:100]
    return messages

# publicなユーザーとグループを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)

