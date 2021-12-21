from enum import auto
from hello.views import message
from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.base import Model

#Message class

class Message (models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE,\
    related_name='message_owner')
  group = models.ForeignKey('Group', on_delete=models.CASCADE)
  content = models.TextField(max_length=1000)
  share_id = models.IntegerField(default=-1)
  good_count = models.IntegerField(default=0)
  share_count = models.IntegerField(default=0)
  pub_date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return str(self.content) + ' (' + str(self.owner) + ')'

  def get_share(self):
    return Message.objects.get(id=self.share_id)

  class Meta:
    ordering = ('-pub_date',)

#group class
class Group(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, \
    related_name='group_owner')
  title = models.CharField(max_length=100)

  def __str__(self):
    return '<' + self.title + '(' + str(self.owner) + ')>'


#Friend class
class Friend(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, \
    related_name='friend_owner')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  group = models.ForeignKey(Group, on_delete=models.CASCADE)

  def __str__(self):
    return str(self.user) + ' (group:"' + str(self.group) + '")'


#Good class
class Good(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, \
    related_name='good_owner')
  message = models.ForeignKey(Message, on_delete=models.CASCADE)

  def __str__(self):
    return 'good for "' + str(self.message) + '" (by ' + \
      str(self.owner) + ')'
      
      
      
      
from django.db import models
# ユーザー認証
from django.contrib.auth.models import User

# ユーザーアカウントのモデルクラス
class Account(models.Model):

    # ユーザー認証のインスタンス(1vs1関係)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 追加フィールド
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    account_image = models.ImageField(upload_to="profile_pics",blank=True)

    def __str__(self):
        return self.user.username
