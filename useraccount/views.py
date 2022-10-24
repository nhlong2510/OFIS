from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . forms import RegisterForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='user:login')
def userlist(request):
    userlist = ''
    if request.user.is_superuser == True:
        userlist = User.objects.filter(is_superuser = False)
        
    return render(request, "opera/users.html", {
        "userlist": userlist,
    })


@login_required(login_url='user:login')
def registerPage(request):
    frm_reg = ''
    reg_result = ''
    if request.user.is_superuser == True:
        frm_reg = RegisterForm()
        if request.POST.get('btnSubmit'):
            frm_reg = RegisterForm(request.POST)
            if frm_reg.is_valid():
                if frm_reg.cleaned_data['password'] == frm_reg.cleaned_data['confirm_password']:
                    user = frm_reg.save()
                    user.set_password(user.password)
                    user.save()

                    reg_result = f'''
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            Account <b>{user.username}</b> has been registered successfully!!!
                            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                    '''
                    return redirect('user:userlist')

    return render(request, 'opera/register.html', {
        'frm_reg': frm_reg,
        'reg_result': reg_result
    })


@login_required(login_url='user:login')
def useredit(request, pk):
    if request.user.is_superuser == True:
        user = User.objects.get(pk=pk)
        result = ''
        if request.POST.get('btnUpdate'):
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            active = request.POST.get('active')
            conf_pass = request.POST.get('confirm_pass')
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.is_active = active
            if password == conf_pass:
                user.set_password(password)
            user.save()
            
            result = """
                <div class="alert alert-sucess" role="alert">
                    account has been updated successfully!!!!
                </div>
            """
            return redirect('user:userlist')
        
    return render(request, 'opera/edit-user.html', {
        "user": user,
        "result": result
    })


def userlogin(request):
    login_result = ''
    if request.user.is_authenticated:
        return redirect('opera:opera')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('opera:opera')
            else:
                login_result='''
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    Username or Password is not correct!!! Please try again!
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                '''
        
        return render(request, 'opera/login.html', {'login_result': login_result})


def userlogout(request):
    logout(request)
    return redirect('user:login')    
