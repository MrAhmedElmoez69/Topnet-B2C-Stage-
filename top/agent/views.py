from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from client.models import ScoreParameters

@login_required
def configure_score_parameters(request):
    parameters = ScoreParameters.objects.all()
    if request.method == 'POST':
        for param in parameters:
            param.poids = request.POST.get(f'param_{param.id}', 0)
            param.objectif = request.POST.get(f'objectif_{param.id}', 0)
            param.save()
      #  return redirect('client:view_score')
    return render(request, 'agent/calculate_score.html', {'parameters': parameters})



