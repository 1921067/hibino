from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Message,Friend,Group,Good
from .forms import GroupCheckForm,GroupSelectForm,\
  FriendsForm,CreateGroupForm,PostForm
from .forms import AccountForm, AddAccountForm #ユーザーアカウントフォーム

# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView # テンプレートタグ
from django.contrib.auth import authenticate
from django.conf import settings
import pandas as pd

df = pd.read_csv('movie_data.csv', encoding='utf-8')

import re
def preprocessor(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)',
                           text)
    text = (re.sub('[\W]+', ' ', text.lower()) +
            ' '.join(emoticons).replace('-', ''))
    return text

df['review'] = df['review'].apply(preprocessor)


import nltk
nltk.download('stopwords')




import numpy as np
import re
from nltk.corpus import stopwords



stop = stopwords.words('english')

def tokenizer(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text.lower())
    text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', '')
    tokenized = [w for w in text.split() if w not in stop]
    return tokenized


def stream_docs(path):
    with open(path, 'r', encoding='utf-8') as csv:
        next(csv)  
        for line in csv:
            text, label = line[:-3], int(line[-2])
            yield text, label


def get_minibatch(doc_stream, size):
    docs, y = [], []
    try:
        for _ in range(size):
            text, label = next(doc_stream)
            docs.append(text)
            y.append(label)
    except StopIteration:
        return None, None
    return docs, y


from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier


vect = HashingVectorizer(decode_error='ignore', 
                         n_features=2**21,
                         preprocessor=None, 
                         tokenizer=tokenizer)

clf = SGDClassifier(loss='log', random_state=1)

doc_stream = stream_docs(path='movie_data.csv')


import pyprind
pbar = pyprind.ProgBar(45)

classes = np.array([0, 1])
for _ in range(45):
    X_train, y_train = get_minibatch(doc_stream, size=1000)
    if not X_train:
        break
    X_train = vect.transform(X_train)
    clf.partial_fit(X_train, y_train, classes=classes)
    pbar.update()





label = {0:'ネガティブ', 1:'ポジティブ'}

from googletrans import Translator




class  AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        "add_account_form":AddAccountForm(),
        }

    # Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        return render(request,"sns/register.html",context=self.params)

    # Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)
        self.params["add_account_form"] = AddAccountForm(data=request.POST)

        # フォーム入力の有効検証
        if self.params["account_form"].is_valid() and self.params["add_account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新
            account.save()

            # 下記追加情報
            # 下記操作のため、コミットなし
            add_account = self.params["add_account_form"].save(commit=False)
            # AccountForm & AddAccountForm 1vs1 紐付け
            add_account.user = account

            # 画像アップロード有無検証
            if 'account_image' in request.FILES:
                add_account.account_image = request.FILES['account_image']

            # モデル保存
            add_account.save()

            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        return render(request,"sns/register.html",context=self.params)
#ログイン
def Login(request):
    # POST
    if request.method == 'POST':
        # フォーム入力のユーザーID・パスワード取得
        ID = request.POST.get('userid')
        Pass = request.POST.get('password')

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            #ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request,user)
                # ホームページ遷移
                return HttpResponseRedirect(reverse('index'))
            else:
                # アカウント利用不可
                return HttpResponse("アカウントが有効ではありません")
        # ユーザー認証失敗
        else:
            return HttpResponse("ログインIDまたはパスワードが間違っています")
    # GET
    else:
        return render(request, 'sns/login.html')


#ログアウト
@login_required
def Logout(request):
    logout(request)
    # ログイン画面遷移
    return HttpResponseRedirect(reverse('Login'))


#ホーム
#@login_required
#def index(request):
    #params = {"UserID":request.user,}
    #return render(request, "sns/index.html",context=params)


#新規登録
class  AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        "add_account_form":AddAccountForm(),
        }

    #Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        return render(request,"sns/register.html",context=self.params)

    #Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)
        self.params["add_account_form"] = AddAccountForm(data=request.POST)

        #フォーム入力の有効検証
        if self.params["account_form"].is_valid() and self.params["add_account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新
            account.save()

            # 下記追加情報
            # 下記操作のため、コミットなし
            add_account = self.params["add_account_form"].save(commit=False)
            # AccountForm & AddAccountForm 1vs1 紐付け
            add_account.user = account

            # 画像アップロード有無検証
            if 'account_image' in request.FILES:
                add_account.account_image = request.FILES['account_image']

            # モデル保存
            add_account.save()

            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        return render(request,"sns/register.html",context=self.params)
      
      
      
      
      
      
      

#indexのレビュー関数
@login_required
def index(request, page=1):
  #publicのユーザーを取得
  (public_user, public_group) = get_public()

  #POST送信時ｎ処理
  if request.method == 'POST':

    #groupのチェックを更新したいときの処理
    #フォームの用意
    checkform = GroupCheckForm(request.user,request.POST)
    #チェックされたgroup名リストにまとめる
    glist = []
    for item in request.POST.getlist('groups'):
      glist.append(item)
    #messageの取得
    messages = get_your_group_message(request.user, \
      glist, page)

  #getアクセス時の処理
  else:
    #フォームの用意
    checkform = GroupCheckForm(request.user)
    #groupのリストを取得
    gps = Group.objects.filter(owner=request.user)
    glist = [public_group.title]
    for item in gps:
      glist.append(item.title)
    #メッセージの取得
    messages = get_your_group_message(request.user, glist, page)

  so = []
  m = '%'

  for my in Message.objects.values('content'):
          for mm in my.values():
            oni = mm
            translator = Translator()
            dst = translator.translate(mm, src='ja', dest='en').text
            example = [dst]
            X = vect.transform(example)
            mm = label[clf.predict(X)[0]]
            ok = np.max(clf.predict_proba(X))*100
            ok = round(ok,2)
            ok = str(ok) + m
            so.append([oni,mm,ok])
  
  fgo = []
  for mn in so:
    if mn not in fgo:
        fgo.append(mn)
            
    
  bla = []   
  ck = []     
  for ss in fgo:
    bla.append(ss[0])
    ck.append([ss[1],ss[2]])     

  
    #共通処理
  params = {
      'UserID':request.user,
      'contents':messages,
      'co':bla,
      'so':ck,
      'check_form':checkform,
  }
  return render(request, 'sns/index.html', params)

@login_required
def groups(request):
  #自分が登録したFriendを取得
  friends = Friend.objects.filter(owner=request.user)

  #POST送信時の処理
  if request.method == 'POST':

    #GROUPメニュー選択じの処理
    if request.POST['mode'] == '__groups_form__':
      #選択したグループ名の取得
      sel_group = request.POST['groups']
      #GROUPを取得
      gp = Group.objects.filter(owner=request.user) \
        .filter(title=sel_group).first()
      #GROUPに含まれるFRIENDの取得
      fds = Friend.objects.filter(owner=request.user) \
        .filter(group=gp)
      print(Friend.objects.filter(owner=request.user))
      #FRIENDのユーザーをリストにまとめる
      vlist = []
      for item in fds:
        vlist.append(item.user.username)
      #フォームの用意
      groupsform = GroupSelectForm(request.user,request.POST)
      friendsform = FriendsForm(request.user, \
        friends=friends, vals=vlist)


    #FRIENｓのチェック時の処理★
    if request.POST['mode'] == '__friends_form__':
      #選択したGROUPの取得
      sel_group = request.POST['group']
      group_obj = Group.objects.filter(title=sel_group).first()
      print(group_obj)
      #チェックしたFRIENDsを取得
      sel_fds = request.POST.getlist('friends')
      #FRIENDsのUsERを取得
      sel_users = User.objects.filter(username__in=sel_fds)
      #Userのリストに含まれるユーザーが登録したFRIENDを取得
      fds = Friend.objects.filter(owner=request.user) \
        .filter(user__in=sel_users)
      #全てのFRIENDにGROUPを設定し保存
      vlist = []
      for item in fds:
        item.group = group_obj
        item.save()
        vlist.append(item.user.username)
      #メッセージ設定
      messages.success(request, ' フレンドを' + \
        sel_group + 'に登録しました。')
      #フォーム用意
      groupsform = GroupSelectForm(request.user, \
        {'groups':sel_group})
      friendsform = FriendsForm(request.user, \
        friends=friends, vals=vlist)


  #GETアクセス時んぼ処理
  else:
    #フォームの用意
    groupsform = GroupSelectForm(request.user)
    friendsform = FriendsForm(request.user, friends=friends, \
                  vals=[])
    sel_group = '-'
    
  #共通処理
  createform = CreateGroupForm()
  params = {
    'UserID':request.user,
    'groups_form':groupsform,
    'friends_form':friendsform,
    'create_form':createform,
    'group':sel_group,
  }
  return render(request, 'sns/groups.html', params)
#★

#FRIENDの追加処理
@login_required
def  add(request):
  #追加するUser取得
  add_name = request.GET['name']
  add_user = User.objects.filter(username=add_name).first()
  #Userが本人のときの処理
  if add_user == request.user:
    messages.info(request, "自分自身をFriendに追加することは\
      出来ません。")
    return redirect(to='/sns/index')

  #PUblicの取得
  (public_user, public_group) = get_public()
  #add-userのFRIENDの数を調べる
  frd_num = Friend.objects.filter(owner=request.user) \
    .filter(user=add_user).count()
  #ゼロより大きければ登録済み
  if frd_num > 0:
    messages.info(request, add_user.username + \
      ' は既に追加されています。')
    return redirect(to='/sns/index')
  
  #ここからFRIENDの登録処理
  frd = Friend()
  frd.owner = request.user
  frd.user = add_user
  frd.group = public_group
  frd.save()
  
  #メッセージ設定
  messages.success(request, add_user.username + ' を追加しました！\
    groupページに移動して、追加したFriendをメンバーに設定してください。')
  return redirect(to='/sns/index')
#グループ作成処理
@login_required
def creategroup(request):
  #GROUPを作り、Userとtitleを設定して保存
  gp = Group()
  gp.owner = request.user
  gp.title = request.user.username + 'の' + request.POST['group_name']
  gp.save()
  messages.info(request, '新しいグループを作成しました。')
  return redirect(to='/sns/groups')


#メッセージポスト処理
@login_required
def post(request):
  #POST送信処理
  if request.method == 'POST':
    #送信内容の取得
    gr_name = request.POST['groups']
    content = request.POST['content']
    #groupの取得
    group = Group.objects.filter(owner=request.user) \
      .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    #messageを作成し設定して保存
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.save()
    #メッセージ設定
    messages.success(request, '新しいメッセージを投稿しました。')
    return redirect(to='/sns/index')

  #GETアクセス時の処理
  else:
    form = PostForm(request.user)

  #共通処理
  params = {
    'UserID':request.user,
    'form':form,
  }
  return render(request, 'sns/post.html', params)

#投稿シェア
@login_required
def share(request, share_id):
  #シェアするメッセージの取得
  share = Message.objects.get(id=share_id)
  print(share)
  #POST送信時処理
  if request.method == 'POST':
    #送信内容取得
    gr_name = request.POST['groups']
    content = request.POST['content']
    #Group取得
    group = Group.objects.filter(owner=request.user) \
      .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    #メッセージを作成して設定
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.share_id = share_id
    msg.save()
    share_msg = msg.get_share()
    share_msg.share_count += 1
    share_msg.save()
    #メッセージ設定
    messages.success(request, 'メッセージをシェアしました。')
    return redirect(to='/sns/index')

  #共通処理
  form = PostForm(request.user)
  params = {
    'UserID':request.user,
    'form':form,
    'share':share,
  }
  return render(request, 'sns/share.html', params)

#goodボタン処理
@login_required
def good(request, good_id):
  #goodするmessageを取得
  good_msg = Message.objects.get(id=good_id)
  #自分がメッセージにgoodした数を調べる
  is_good = Good.objects.filter(owner=request.user) \
    .filter(message=good_msg).count()
  #ゼロより大きければ既にgood済み
  if is_good > 0:
    messages.success(request, '既にメッセージにはgoodしています')
    return redirect(to='/sns/index')

  #messageのgoodCOUNTを１増やす
  good_msg.good_count +=1
  good_msg.save()
  #good作成し設定して保存
  good = Good()
  good.owner = request.user
  good.message = good_msg
  good.save()
  #メッセージ設定
  messages.success(request, 'メッセージにgoodしました。')
  return redirect(to='/sns/index')


#指定されたグループおよび検索文字によるmessageの取得
def get_your_group_message(owner, glist, page):
  page_num = 10 #ページあたりの表示数
  #PUblicの取得
  (public_user,public_group) = get_public()
  #チェックされたgroupの取得
  groups = Group.objects.filter(Q(owner=owner) \
          |Q(owner=public_user)).filter(title__in=glist)
  #groupに含まれるFRIENDの取得
  me_friends = Friend.objects.filter(group__in=groups)
  #FriendのUserをリストにまとめる
  me_users = []
  for f in me_friends:
    me_users.append(f.user)
  #UserのUserが作ったgroupの取得
  his_groups = Group.objects.filter(owner__in=me_users)
  his_friends = Friend.objects.filter(user=owner) \
    .filter(group__in=his_groups)
  me_groups = []
  for hf in his_friends:
    me_groups.append(hf.group)
  #groupがgroupsに含まれるか、me-groupsに含まれる
  messages = Message.objects.filter(Q(group__in=groups) \
    |Q(group__in=me_groups))
  #ページネーションで指定ページを取得
  page_item = Paginator(messages, page_num)
  return page_item.get_page(page)

#PUblicなUserとgroupを取得
def get_public():
  public_user = User.objects.filter(username='public').first()
  public_group = Group.objects.filter \
          (owner=public_user).first()
  return (public_user, public_group)



import requests
from bs4 import BeautifulSoup
import re


def News(request):

  a = request.POST.get('name')
    

  if not a:
    a = ''
    mm = ''
    ok = ''
    URL = "https://news.yahoo.co.jp/"
    ti = '主要'
    
  else:
    a = str(a)
    m = '%'
    translator = Translator()
    dst = translator.translate(a, src='ja', dest='en').text
    example = [dst]
    X = vect.transform(example)
    mm = label[clf.predict(X)[0]]
    ok = np.max(clf.predict_proba(X))*100
    bb = round(ok,2)
    ok = str(bb) + m
    
    if mm == 'ポジティブ' and bb >= 80:
        URL = "https://news.yahoo.co.jp/categories/sports"
        ti = 'スポーツ'
        
    elif mm == 'ポジティブ' and 80 > bb >= 70:
        URL = "https://news.yahoo.co.jp/categories/entertainment"
        ti = 'エンタメ'
      
    elif mm == 'ポジティブ' and 70 > bb >= 60:
        URL = "https://news.yahoo.co.jp/categories/it"
        ti = 'IT'  
        
    elif mm == 'ポジティブ' and 60 > bb >= 50:
        URL = "https://news.yahoo.co.jp/categories/science" 
        ti = '科学'
        
    elif mm == 'ネガティブ' and 60 > bb >= 50:
        URL = "https://news.yahoo.co.jp/categories/domestic" 
        ti = '国内' 
      
    elif mm == 'ネガティブ' and 70 > bb >= 60:
        URL = "https://news.yahoo.co.jp/categories/business"  
        ti = '経済'
        
    elif mm == 'ネガティブ' and 80 > bb >= 70:
        URL = "https://news.yahoo.co.jp/categories/world" 
        ti = '国際' 
    
    elif mm == 'ネガティブ' and bb >= 80:
        URL = "https://news.yahoo.co.jp/categories/local" 
        ti = '地域' 
    
      
  

  res = requests.get(URL)


  soup = BeautifulSoup(res.text, "html.parser")
  
  topic = soup.find(class_="sc-jGFFOr Pplqh")

  data_list = topic.find_all(href=re.compile("news.yahoo.co.jp/pickup"))

  headline_link_list = [data.attrs["href"] for data in data_list]

  mylist = []

  web = []


  for headline_link in headline_link_list:

    summary = requests.get(headline_link)

    summary_soup = BeautifulSoup(summary.text, "html.parser")

    summary_find = summary_soup.find('p', class_='sc-dTSiUb fCZKLk')

    summary_found = summary_soup.find('p', class_='sc-eQvJSV cMIDqS highLightSearchTarget')

    mylist.append(summary_find.text)
    web.append(summary_found.text)
    
    
  web.reverse()
  params = { 
        'UserID':request.user,
        'title': mylist,
        'subtitle': web,
        'name': a,
        'emo':mm,
        'par':ok,
        'tit':ti
        }

  return render(request, 'sns/News.html', params)


