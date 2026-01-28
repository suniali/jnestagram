from django.views.generic import TemplateView

class NotFoundView(TemplateView):
    template_name = '404.html'

    def get(self,request,*args,**kwargs):
        context=super().get_context_data(**kwargs)
        return  self.render_to_response(context,status=404)

class InternalServerErrorView(TemplateView):
    template_name = '500.html'

    def dispatch(self, request, *args, **kwargs):
        return self.render_to_response({}, status=500)