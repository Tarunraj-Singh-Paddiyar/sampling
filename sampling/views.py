from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from .models import Order, register_user, sampling_stock, Designs
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.mail import send_mail
import random
import json
from django.contrib.auth.models import Group,  User
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from openpyxl import Workbook

def sampling(request):
    return render(request, 'sampling.html')

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')

        #OTP
        verification_code = ''.join(random.choices('0123456789', k=4))

        # Check password length
        if len(password) < 8:
            messages.error(request, 'Length of the password should be greater than 8 characters.')
            return redirect('signup')
                
        #hashed password
        hashed_password = make_password(password)

        # Store everything in session
        request.session['verification_code'] = verification_code
        request.session['name'] = name
        request.session['brand'] = brand
        request.session['email'] = email
        request.session['phone'] = phone
        request.session['username'] = username
        request.session['password'] = hashed_password


         # Send verification code to user's email
        send_mail(
            'Verification Code',
            f'Your verification code is: {verification_code}',
            'test4sampling@outlook.com',
            [email],
            fail_silently=False,
        )

        return redirect('verify')

    return render(request, 'signup.html')

def verify(request):
    if request.method == 'POST':
        # Get verification code from form
        entered_code = request.POST.get('OTP')

        # Get verification code from session
        verification_code = request.session.get('verification_code')

        # Check if entered code matches verification code
        if entered_code == verification_code:
            print("code verified")
            # Code matches, proceed to create user
            name = request.session.get('name')
            brand = request.session.get('brand')
            email = request.session.get('email')
            phone = request.session.get('phone')
            username = request.session.get('username')
            password = request.session.get('password')

            print("code is reaching till here.")
            new_user = register_user.objects.create(name = name, brand = brand, email=email, phone = phone, username=username,  password=password)
            new_user.save()
            print("New user has been created with the username", username)
            # Redirect to success page or signin page
            del request.session['name']
            del request.session['brand']
            del request.session['email']
            del request.session['phone']
            del request.session['password']
            return redirect('designs')
        else:
            print("code not verified")
            # Code does not match, show error message
            messages.error(request, 'Invalid verification code')
            return redirect('verify')  # Redirect back to registration page
    else:
        return render(request, 'verify.html')

def customeruserexists(request):
    try:
        username = request.session['customerusername']
        username_exists = register_user.objects.get(username=username)
        return username, username_exists
    except:
        username,username_exists = None, None
        return username, username_exists

def signin(request):
    username , customerexists = customeruserexists(request)
    if username!= None and customerexists != None:
        return redirect('customerdashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(username, password)
            try:
                user = register_user.objects.get(username=username)
            except register_user.DoesNotExist:
                user = None
                messages.error(request, 'User Does Not Exists')
                return redirect('signin')

            if user is not None and check_password(password,user.password):
                request.session['customerusername'] = user.username
                return redirect('designs')  # Redirect to success page
            else:
                # Invalid credentials, show error message
                messages.error(request, 'Invalid username - password combination')
                return render(request, 'signin.html', {'invalid_creds': True})  # Render signin page with error message
        else:
            return render(request, 'signin.html')
    
def generateorderno():
    try:
        last_order = Order.objects.order_by('-orderno').first()  # Order by descending ID and get first
    except:
        last_order = None
    if last_order != None:
        neworderno = last_order.orderno+1
    else:
        neworderno = 1000
    return neworderno
    
def designs(request):
    username , customerexists = customeruserexists(request)
    if customerexists != None and username!=None:
        if request.method == 'POST' and customerexists:
            selected_samples =  request.POST.get('selectedSamples')
            request.session['selected_samples'] = selected_samples
            orderno = generateorderno()
            request.session['orderno'] = orderno
            # print(username, customerexists, name, brand, email, phone, sample_type, selected_samples, orderno )
            if (orderno and selected_samples):
                return redirect('orderpage')
            else:
                return HttpResponse('Invalid form data. Please fill in all required fields. ')

        else:
            if customerexists:
                designs = Designs.objects.all()
                context = {
                    'designs':designs,
                    'username' : username
                }
                return render(request, 'designs.html', context)
    else:
        return redirect('signin')

def get_design_details(request, design_name):
    try:
        # Assuming Design model has fields like title, image_url, and description
        design = Designs.objects.get(name=design_name)
        design_details = {
            'Name': design.name,
            'image_url': design.image.url,
            'description': design.description
        }
        return JsonResponse(design_details)
    except Designs.DoesNotExist:
        return JsonResponse({'error': 'Design not found'}, status=404)

def success(request):
    return redirect('customerdashboard')

def customerlogout(request):
    try:
        del request.session['customerusername']
        # del request.session['key2']
        return redirect('sampling')
    except:
        return redirect('sampling')

def stafflogout(request):
    try:
        del request.session['staffusername']
        # del request.session['key2']
        return redirect('sampling')
    except:
         return redirect('sampling')

def check_username_availability(request):
    username = request.GET.get('username', '')
    user_exists = register_user.objects.filter(username=username).exists()
    print(user_exists)
    return JsonResponse({'available': not user_exists})

def staffuserexists(request):
    try:
        username = request.session['staffusername']
        username_exists = User.objects.get(username=username)
    except:
        username = None
        username_exists = None
    return username, username_exists

def checkgroup(user):
            user_groups = user.groups.all()
            if Group.objects.filter(name='Sampling Office').intersection(user_groups):
                group = "Sampling Office"
                return group
            elif Group.objects.filter(name='Manufacture').intersection(user_groups):
                group = "Manufacture"
                return group
            elif Group.objects.filter(name='Marketing').intersection(user_groups):
                group = "Marketing"
                return group
            elif Group.objects.filter(name='QA_Department').intersection(user_groups):
                group = "QA Department"
                return group
            else:
                return HttpResponse("You don't have access to any dashboard.")   

def staff_signin(request):
    username,staffexists = staffuserexists(request)
    print(username, staffexists)
    if (username != None) and (staffexists != None):
        user = User.objects.get(username=username)
        print(user)
        group = checkgroup(user)
        if(group == "Sampling Office"):
                    return redirect("sampling_office_dashboard")   
        elif(group == "Manufacture"):
                    return redirect("manufacturing_dashboard")   
        elif(group == "Marketing"):
                    return redirect("marketing_dashboard")   
        elif(group == "QA_department"):
                    return redirect("qa_dashboard")  
        else:
                    return HttpResponse("You don't have access to any dashboard!") 
    else:
        if request.method == 'POST':
            username = request.POST.get('susername')
            password = request.POST.get('spassword')
            user = authenticate(request, username=username, password=password)
            print(username, user)
            print(type(username))
            print(type(user))
            if user is not None:
                group = checkgroup(user)  
                if(group == "Sampling Office"):
                    request.session['staffusername'] = username
                    return redirect("sampling_office_dashboard")   
                elif(group == "Manufacture"):
                    request.session['staffusername'] = username
                    return redirect("manufacturing_dashboard")   
                elif(group == "Marketing"):
                    request.session['staffusername'] = username
                    return redirect("marketing_dashboard")   
                elif(group == "QA_department"):
                    request.session['staffusername'] = username
                    return redirect("qa_dashboard")   
                else:
                    return HttpResponse("You don't have access to any dashboard!")   
            else:
                return HttpResponse("May be your username or password is wrong. Or may be you are not a valid staff member!")       
        else:
            return render(request, 'staff_signin.html')
     
def sampling_office_dashboard(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
        sampling_stocks = sampling_stock.objects.all()
        username = str(request.session['staffusername']).capitalize
        context = {
                'sampling_stocks' : sampling_stocks,
                'username':username
            }
        return render(request,'dashboards/sampling-office-dashboard.html', context)
    else:
        return redirect("staff_signin") 

def updatestock(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            if request.method == 'POST':
                data = json.loads(request.body)
                print(data)
                designid = data.get('designId')
                # print(designid)
                action = data.get('action')
                addremove = data.get('addremove')
                try:
                    existing_item = sampling_stock.objects.get(designid=designid)
                except ObjectDoesNotExist:
                    return HttpResponse("Sampling stock with the given design ID does not exist.", status=404)
                if(existing_item!=None):
                    if(action == "add"):
                        existing_item.quantity += int(addremove)
                        existing_item.save()
                    elif(action == "remove"):
                        existing_item.quantity -= int(addremove)
                        existing_item.save()
                    else:
                        return redirect("sampling_office_dashboard")
                    return JsonResponse({'success': True, 'updated_quantity': existing_item.quantity})
                else:
                    return HttpResponse("Does Not exists")
            else:
                return JsonResponse({'error': 'Invalid request method'}, status=400)
    else:
        return redirect('staff_signin')
 
def showorders(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            Orders = Order.objects.all()
            context={
                "Orders":Orders
            }
            return render(request,'dashboards/sampling office features/showorders.html', context)
    else:
        return redirect('staff_signin')

def addnewitems(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            if request.method == 'POST':
                designid = request.POST.get('designid')
                rackno = request.POST.get('rackno')
                quantity = request.POST.get('quantity')
                if(designid and rackno and quantity):
                    try:
                        item_exist = sampling_stock.objects.get(designid=designid)
                    except:
                        item_exist = None
                    if(item_exist != None):
                        return HttpResponse("The Item already Exists")
                    else:
                        new_item = sampling_stock(designid = designid,  rackno = rackno, quantity = quantity)
                        new_item.save()
                        return redirect("addnewitems")
                else:
                    return HttpResponse("The Input Data is Invalid.")
            else:    
                return render(request, 'dashboards/sampling office features/addnewitems.html')
    else:
        return redirect('staff_signin')
    
def deleteitems(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            if request.method == 'POST':
                designid = request.POST.get('designid')
                print(designid)
                if(designid):
                    try:
                        item_exist = sampling_stock.objects.get(designid=designid)
                        print(designid)
                    except:
                        item_exist = None
                        print(designid)
                        return HttpResponse("The Given Item with the Design ID doesn't exists in the database.")
                    if(item_exist != None):
                        print(designid)
                        item_exist.delete()
                        return redirect("deleteitems")
                    else:
                        return HttpResponse("The Given Item with the Design ID doesn't exists in the database.")                
            else:    
                return render(request, 'dashboards/sampling office features/deleteitems.html')
    else:
        return redirect('staff_signin')

def updatestatus(request, orderno):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            try:
                order = get_object_or_404(Order, orderno=orderno)
                selected_samples = order.selected_samples.split(',')
                context = {
                    'orderno': orderno,
                    'username': order.username,
                    'name': order.name,
                    'brand': order.brand,
                    'email': order.email,
                    'phone': order.phone,
                    'sample_type': order.sample_type,
                    'selected_samples': selected_samples,
                    'completestatus': order.completestatus,
                }
            except (Order.DoesNotExist, ValueError):
                return HttpResponse("Order not found or invalid order number")

            if request.method == 'POST':
                order.completestatus = True  # Assuming completed status is True
                order.save()
                return redirect('showorders')  # Redirect to a relevant page after successful update
            else:
                return render(request, 'dashboards/sampling office features/updatestatus.html', context)
    else:
        return redirect('staff_signin')

def completedorders(request):
    username,staffexists = staffuserexists(request)
    if username!= None and staffexists != None:
            orders = Order.objects.all()
            context={
                "orders":orders
            }
            return render(request,'dashboards/sampling office features/completed_status.html', context)
    else:
        return redirect('staff_signin')
    
def customerdashboard(request):
    username , customerexists = customeruserexists(request)
    if customerexists != None and username!=None:
        selected_samples_by_orders = []
        user = register_user.objects.get(username = username)
        name = user.name
        ordersbycustomer = Order.objects.filter(username = username).order_by("-orderno")
        # print(ordersbycustomer)
        for order in ordersbycustomer:
            # print(order)
            ss = order.selected_samples
            ss_list = ss.split(',')
            # print(ss_list)
            selected_samples_by_orders += [ss_list]
        selected_samples_by_orders = selected_samples_by_orders[::-1]
        # print(selected_samples_by_orders)
        context={
                'orders' : ordersbycustomer,
                'name' : name,
                'ssbo':selected_samples_by_orders,
        }
        return render(request,'dashboards/customerdashboard.html', context)
    else:
        return redirect('signin')
    
def download_in_excel(request, orderno):
    order = get_object_or_404(Order, orderno=orderno)
    allsamples = order.selected_samples.split(',')
    brandname = order.brand

    wb = Workbook()
    sheet = wb.active

    sheet.append([brandname, orderno])

    for sample in allsamples:
        sheet.append([' ', sample])

    # Set content type and return response with filename
    response = HttpResponse(content_type='application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={brandname}_{orderno}.xlsx'
    wb.save(response)
    return response

def mycart(request):
    username , customerexists = customeruserexists(request)
    if customerexists != None and username!=None:
        selected_samples = request.session['selected_samples']
        selected_samples = selected_samples.split(",")
        print(selected_samples)
        all_designs = []
        for sample in selected_samples:
            sample_obj = Designs.objects.get(name = sample)
            all_designs.append(sample_obj)
        context = {
            'all_designs':all_designs
        }
        return render(request, 'dashboards/mycart.html' ,context )
    else:
        return redirect('signin')

def orderpage(request):
    username , customerexists = customeruserexists(request)
    if customerexists != None and username!=None:
        try:
            selected_samples = request.session['selected_samples']
            orderno = request.session['orderno']
        except:
            return HttpResponse("Your session has been expired")
        username_object = register_user.objects.get(username=username)
        selected_samples = request.session['selected_samples']
        orderno = request.session['orderno']
        if request.method == "POST":
            name = request.POST.get("name")
            brand = request.POST.get("brand")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            sampletype = request.POST.get("select-type")
            address = request.POST.get("address")
            new_order = Order(orderno=orderno,username=username,  name=name, brand=brand, email=email, phone = phone, selected_samples=selected_samples, sampletype=sampletype,address=address)
            new_order.save()
            del request.session['selected_samples']
            del request.session['orderno']
            return redirect('customerdashboard')
        else:
            dname = username_object.name
            dbrand = username_object.brand
            demail = username_object.email
            dphone = username_object.phone
            context = {
                'orderno':orderno,
                'selected_samples':selected_samples,
                'name':dname,
                'brand':dbrand,
                'email' :demail,
                'phone': dphone
            }
            return render(request, 'dashboards/orderpage.html', context)
    else:
         return redirect('signin')