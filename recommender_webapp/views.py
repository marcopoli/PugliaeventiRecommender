from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_protect

from recommender_webapp.forms import ProfileForm, UserRegisterForm
from recommender_webapp.models import Comune, Distanza, Place, Mood, Companionship
from pugliaeventi import constant


@csrf_protect
def user_login(request):
    if request.POST:
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None and user.is_active:
            print('User login: Email: ' + email + '     Password: ' + password)
            print(request.POST)
            login(request, user)
            return render(request, 'base.html', {'email_splitted': user.email.split('@')[0]})
        else:
            return render(request, 'base.html', {'message': 'Username or Password wrong!'})
    else:
        return render(request, '404.html')


def user_logout(request):
    logout(request)
    return HttpResponse()


@csrf_protect
def user_signup(request):
    user_form = UserRegisterForm(request.POST or None)
    profile_form = ProfileForm(request.POST or None)

    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password')
        location = profile_form.cleaned_data.get('location')
        user.set_password(password)
        user.save()

        location_found = Comune.objects.filter(nome__iexact=location)
        user.profile.location = location_found.first().nome
        user.save()

        new_user = authenticate(username=user.email, password=password)
        login(request, new_user)
        return redirect('/')

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, "signup.html", context)


def profile_configuration(request):
    if request.user.is_authenticated:

        """
        user_contexts = []
        for (mood_name, mood_index) in Mood.choices():
            for (comp_name, comp_index) in Companionship.choices():
                # user_context = str(mood_index) + str(comp_index)
                user_context = (mood_name, comp_name)
                user_contexts.append(user_context)
        """

        close_places = []
        user_location = request.user.profile.location
        distances_in_range = Distanza.objects.filter(cittaA=user_location, distanza__lte=constant.KM_RANGE_CONFIGURATION).order_by('distanza')

        user_location_places = Place.objects.filter(location=user_location)
        for place in user_location_places:
            close_places.append(place)

        for distance in distances_in_range:
            places = Place.objects.filter(location=distance.cittaB)
            for place in places:
                close_places.append(place)

    else:
        return redirect('/')

    context = {
        #'contexts': user_contexts,
        'places': close_places
    }

    return render(request, "profile_configuration.html", context)


def add_rating(request):
    if request.user.is_authenticated:
        pass

    else:
        return redirect('/')

    context = {
        'contexts': None,
        'places': None
    }

    return render(request, "profile_configuration.html", context)