from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Presence
from datetime import date, datetime
 
class HomeView(LoginRequiredMixin, TemplateView):
    # テンプレートの定義
    template_name = 'home.html'
    # 非ログイン時にリダイレクトされるURL
    login_url = '/accounts/login/'
 
 
class PushTimecard(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # POSTでリクエストを受けてから実行するメソッド
    def post(self, request, *args, **kwargs):
        push_type = request.POST.get('push_type')
 
        is_presented = Presence.objects.filter(
            user = request.user,
            presence_time__date = date.today()
        ).exists()
        is_left = Presence.objects.filter(
             user = request.user,
             leave_time__date = date.today()
         ).exists()
 
        response_body = {}
        if push_type == 'presence' and not is_presented:
            # 出勤したユーザーデータを取得してDBに保存する
            presence = Presence(user=request.user)
            presence.save()
            response_time = presence.presence_time
            response_body = {
                'result': 'success',
                'presence_time': response_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        elif push_type == 'leave' and not is_left:
            if is_presented:
                # 退勤するユーザーデータを条件つき検索して取得する
                presence = Presence.objects.filter(
                    user = request.user,
                    presence_time__date = date.today()
                )[0]
                # 退勤時間を新しく取得
                presence.leave_time = datetime.now()
                presence.save()
                response_time = presence.leave_time
                response_body = {
                    'result': 'success',
                    'leave_time': response_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else: # 出勤していない場合
                response_body = {
                    'result': 'not_presented',
                }
        if not response_body:
            response_body = {
                'result': 'already_exists'
            }
        return JsonResponse(response_body)

class PresenceRecords(LoginRequiredMixin, TemplateView):
    template_name = 'presence_records.html'
    login_url = '/accounts/login'
    def get(self, request, *args, **kwargs):
        today = datetime.today()
        
        # 指定したパラメータを受け取る
        search_param = request.GET.get('year_month')
        if search_param:
            search_params = list(map(int, search_param.split('-')))
            search_year = search_params[0]
            search_month = search_params[1]
        else:
            search_year = today.year
            search_month = today.month

        # データを指定した月日で絞り込む
        month_presence = Presence.objects.filter(
            user = request.user,
            presence_time__year = search_year,
            presence_time__month = search_month
        ).order_by('presence_time')
 
        # context用のデータに変形
        presence_context = []
        for presence in month_presence:
            presence_time = presence.presence_time
            leave_time = presence.leave_time
            if leave_time:
                leave_time = leave_time.strftime('%H:%M:%S')
            else:
                if presence_time.date() == today.date():
                    leave_time = None
                else:
                    leave_time = 'not_pushed' 
            day_presence = {
                'date': presence_time.strftime('%Y-%m-%d'),
                'presence_at': presence_time.strftime('%H:%M:%S'),
                'leave_at': leave_time
            }
            presence_context.append(day_presence)
 
        context = {'presence_records': presence_context}
        # Templateにcontextを含めてレスポンスを返す
        return self.render_to_response(context)