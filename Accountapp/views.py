from django.shortcuts import render
from django.views import View

class DemoView(View):
    def get(self, request):
        # Render a template with some context
        context = {
            'message': 'Hello, this is a demo view!'
        }
        return render(request, 'demo_template.html', context)

    def post(self, request):
        # Handle POST request logic here
        data = request.POST.get('data', '')
        return render(request, 'demo_template.html', {'data': data})
