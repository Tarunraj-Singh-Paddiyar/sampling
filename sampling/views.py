from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from .models import Order, register_user, sampling_stock, Designs, Bulk_Order
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
    try:
        del request.session['selected_samples']
        return render(request, 'sampling.html')
    except:
        return render(request, 'sampling.html')


def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # OTP
        verification_code = ''.join(random.choices('0123456789', k=4))

        # Check password length
        if len(password) < 8:
            messages.error(
                request, 'Length of the password should be greater than 8 characters.')
            return redirect('signup')

        # hashed password
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
            new_user = register_user.objects.create(
                name=name, brand=brand, email=email, phone=phone, username=username,  password=password)
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
        username, username_exists = None, None
        return username, username_exists


def signin(request):
    username, customerexists = customeruserexists(request)
    if username != None and customerexists != None:
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

            if user is not None and check_password(password, user.password):
                request.session['customerusername'] = user.username
                return redirect('designs')  # Redirect to success page
            else:
                # Invalid credentials, show error message
                messages.error(
                    request, 'Invalid username - password combination')
                # Render signin page with error message
                return render(request, 'signin.html', {'invalid_creds': True})
        else:
            return render(request, 'signin.html')


def generateorderno():
    try:
        last_order_sampling = Order.objects.order_by('-orderno').first()  
        last_orderno_sampling = last_order_sampling.orderno 
        print("Sampling Latest Orderno", last_orderno_sampling)
    except:
        last_orderno_sampling = 0
    try:
        last_order_bulk = Bulk_Order.objects.order_by('-orderno').first()  
        last_orderno_bulk = last_order_bulk.orderno  
        print("Sampling Latest Orderno", last_orderno_bulk)
    except:
        last_orderno_bulk = 0
    if(last_orderno_sampling or last_orderno_bulk ):
        latest_orderno = max(last_orderno_bulk, last_orderno_sampling)
        return latest_orderno+1
    else:
        return 1000


def designs(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        if request.method == 'POST' and customerexists:
            order_type = request.POST.get('order_type')
            request.session['order_type'] = order_type
            bulk_order = request.POST.get('bulk_order')
            request.session['bulk_order'] = bulk_order
            print(bulk_order)
            selected_samples = request.POST.get('selectedSamples')
            print("Selected Samples is... ", selected_samples)
            request.session['selected_samples'] = selected_samples
            # print(username, customerexists, name, brand, email, phone, sample_type, selected_samples, orderno )
            if (selected_samples):
                return redirect('sampling_order')
            else:
                return HttpResponse('Invalid form data. Please fill in all required fields')

        else:
            if customerexists:
                designs = Designs.objects.all()
                context = {
                    'designs': designs,
                    'username': username
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
            'shade_color': design.shade_color,
            'width': design.width,
            'fabric_type': design.fabric_type,
            'GSM_': design.GSM,
            'pick': design.pick,
            'weave': design.weave,
            'finish': design.finish,
            'description': design.description,
        }
        return JsonResponse(design_details)
    except Designs.DoesNotExist:
        return JsonResponse({'error': 'Design not found'}, status=404)


def success(request):
    return redirect('customerdashboard')


def customerlogout(request):
    try:
        del request.session['customerusername']
        request.session['selected_samples'] = ''
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
    data = json.loads(request.body)
    username = data.get('username')
    if(len(username) < 8):
        return JsonResponse({'available': -1})
    else:       
        user_exists = register_user.objects.filter(username=username).exists()
        if(user_exists):
            return JsonResponse({'available': 0})
        else:
            return JsonResponse({'available': 1})


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
    username, staffexists = staffuserexists(request)
    print(username, staffexists)
    if (username != None) and (staffexists != None):
        user = User.objects.get(username=username)
        print(user)
        group = checkgroup(user)
        if (group == "Sampling Office"):
            return redirect("sampling_office_dashboard")
        elif (group == "Manufacture"):
            return redirect("manufacturing_dashboard")
        elif (group == "Marketing"):
            return redirect("marketing_dashboard")
        elif (group == "QA_department"):
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
                if (group == "Sampling Office"):
                    request.session['staffusername'] = username
                    return redirect("sampling_office_dashboard")
                elif (group == "Manufacture"):
                    request.session['staffusername'] = username
                    return redirect("manufacturing_dashboard")
                elif (group == "Marketing"):
                    request.session['staffusername'] = username
                    return redirect("marketing_dashboard")
                elif (group == "QA_department"):
                    request.session['staffusername'] = username
                    return redirect("qa_dashboard")
                else:
                    return HttpResponse("You don't have access to any dashboard!")
            else:
                return HttpResponse("May be your username or password is wrong. Or may be you are not a valid staff member!")
        else:
            return render(request, 'staff_signin.html')


def sampling_office_dashboard(request):
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        sampling_stocks = sampling_stock.objects.all()
        username = str(request.session['staffusername']).capitalize
        context = {
            'sampling_stocks': sampling_stocks,
            'username': username
        }
        return render(request, 'dashboards/sampling-office-dashboard copy.html', context)
    else:
        return redirect("staff_signin")


def updatestock(request):
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        if request.method == 'POST':
            data = json.loads(request.body)
            print(data)
            designid = data.get('designId')
            # print(designid)
            action = data.get('action')
            addremove = data.get('addremove')
            try:
                existing_item = sampling_stock.objects.get(
                    designid=designid)
            except ObjectDoesNotExist:
                return HttpResponse("Sampling stock with the given design ID does not exist.", status=404)
            if (existing_item != None):
                if (action == "add"):
                    existing_item.quantity += int(addremove)
                    existing_item.save()
                elif (action == "remove"):
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
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        Orders = Order.objects.filter(completestatus = False)
        bulkOrders = Bulk_Order.objects.filter(completestatus = False)
        context = {
            "Orders": Orders, 
            'bulkOrder':bulkOrders
        }
        return render(request, 'dashboards/sampling office features/showorders.html', context)
    else:
        return redirect('staff_signin')


def addnewitems(request):
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        if request.method == 'POST':
            designid = request.POST.get('designid')
            rackno = request.POST.get('rackno')
            quantity = request.POST.get('quantity')
            if (designid and rackno and quantity):
                try:
                    item_exist = sampling_stock.objects.get(
                        designid=designid)
                except:
                    item_exist = None
                if (item_exist != None):
                    return HttpResponse("The Item already Exists")
                else:
                    new_item = sampling_stock(
                        designid=designid,  rackno=rackno, quantity=quantity)
                    new_item.save()
                    return redirect("addnewitems")
            else:
                return HttpResponse("The Input Data is Invalid.")
        else:
            return render(request, 'dashboards/sampling office features/addnewitems.html')
    else:
        return redirect('staff_signin')


def deleteitems(request):
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        if request.method == 'POST':
            designid = request.POST.get('designid')
            print(designid)
            if (designid):
                try:
                    item_exist = sampling_stock.objects.get(
                        designid=designid)
                    print(designid)
                except:
                    item_exist = None
                    print(designid)
                    return HttpResponse("The Given Item with the Design ID doesn't exists in the database.")
                if (item_exist != None):
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
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        typeofOrder = ""
        try:
            order = get_object_or_404(Order, orderno=orderno)
            typeofOrder = "sample"
        except:
            order = get_object_or_404(Bulk_Order, orderno = orderno)
            typeofOrder = "bulk"
        if(typeofOrder == "sample"):
            selected_samples = order.selected_samples.split(',')
            context = {
                'typeofOrder':typeofOrder,
                'orderno': orderno,
                'username': order.username,
                'name': order.name,
                'email': order.email,
                'phone': order.phone,
                'sampletype': order.sampletype,
                'selected_samples': selected_samples,
                'completestatus': order.completestatus,
            }
        elif(typeofOrder == "bulk"):
            context = {
                'typeofOrder':typeofOrder,
                'orderno': orderno,
                'username': order.username,
                'name': order.name,
                'email': order.email,
                'phone': order.phone,
                'length':order.length,
                'width':order.width,
                'selected_design': order.selected_design,
                'completestatus': order.completestatus,
            }

        if request.method == 'POST':
            order.completestatus = True  # Assuming completed status is True
            order.save()
            # Redirect to a relevant page after successful update
            return redirect('showorders')
        else:
            return render(request, 'dashboards/sampling office features/updatestatus.html', context)
    else:
        return redirect('staff_signin')


def completedorders(request):
    username, staffexists = staffuserexists(request)
    if username != None and staffexists != None:
        orders = Order.objects.filter(completestatus = True)
        bulkorders = Bulk_Order.objects.filter(completestatus = True)
        context = {
            "orders": orders,
            "bulkOrders":bulkorders
        }
        return render(request, 'dashboards/sampling office features/completed_status.html', context)
    else:
        return redirect('staff_signin')


def customerdashboard(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        user = register_user.objects.get(username=username)
        name = user.name
        samplingordersbycustomer = Order.objects.filter(
            username=username).order_by("-orderno")
        bulkorderbycustomer = Bulk_Order.objects.filter(
            username=username).order_by("-orderno")
        print(bulkorderbycustomer)
        
        context = {
            'orders': samplingordersbycustomer,
            'bulkorders': bulkorderbycustomer,
            'name': name,
            
        }
        return render(request, 'dashboards/customerdashboard.html', context)
    else:
        return redirect('signin')


def download_in_excel(request, orderno):
    order = get_object_or_404(Order, orderno=orderno)
    allsamples = order.selected_samples.split(',')

    wb = Workbook()
    sheet = wb.active

    sheet.append([orderno])

    for sample in allsamples:
        sheet.append([' ', sample])

    # Set content type and return response with filename
    response = HttpResponse(
        content_type='application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={orderno}.xlsx'
    wb.save(response)
    return response


def get_selected_samples(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        if request.method == 'POST' and customerexists:
            data = json.loads(request.body)
            print("Data is",data)
            selected_samples = data.get('selected_samples')
            request.session['selected_samples'] = selected_samples
            session = {
                'selected_samples': selected_samples
            }
            print("The value of Selected Samples is in get selected samples in Post",selected_samples)
            return JsonResponse(session)
        else:
            try: 
                selected_samples = request.session['selected_samples']
            except:
                selected_samples = ''
            print("In Get selected Samples Else",selected_samples)
            session = {
                'selected_samples': selected_samples
            }
            return JsonResponse(session)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def directbulkorder(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        if (request.method == "POST"):
            username_object = register_user.objects.get(username=username)
            bulkselecteddesign = request.POST.get('bulkselecteddesign')
            designobject = Designs.objects.get(name= bulkselecteddesign)
            print(designobject)
            imageurl = designobject.image
            print(imageurl)
            bulklength = request.POST.get('bulklength')
            bulkwidth = request.POST.get('bulkwidth')
            orderno = generateorderno()
            name = username_object.name
            email = username_object.email
            phone = username_object.phone
            new_bulk_order = Bulk_Order(image = imageurl, orderno=orderno, username=username, name=name, email=email,
                                        phone=phone, selected_design=bulkselecteddesign, length=bulklength, width=bulkwidth)
            new_bulk_order.save()
            return render(request, 'dashboards/orderplaced.html')
        else:
            return HttpResponse('Bad Request')
    else:
        return redirect('signin')


def mycart(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        try:
            selected_samples = request.session['selected_samples']
            if(len(selected_samples)==0):
                return render(request, 'dashboards/nothingtoshow.html')
        except:
            return render(request, 'dashboards/nothingtoshow.html')
        if (type(selected_samples) == str):
            selected_samples = selected_samples.split(",")
        
        print(selected_samples)
        if (request.method == "POST" and customerexists):
            designtoremove = request.POST.get('designtoremove')
            selected_samples.remove(designtoremove)
            request.session['selected_samples'] = selected_samples
            return redirect('mycart')
        else:
            all_designs = []
            print("The value of selected_samples is", selected_samples)
            for sample in selected_samples:
                sample_obj = Designs.objects.get(name=sample)
                all_designs.append(sample_obj)
            context = {
                'all_designs': all_designs
            }
            return render(request, 'dashboards/mycart.html', context)
    else:
        return redirect('signin')


def sampling_order(request):
    username, customerexists = customeruserexists(request)
    if customerexists != None and username != None:
        try:
            selected_samples = request.session['selected_samples']
        except:
            return HttpResponse("Your session has been expired")
        username_object = register_user.objects.get(username=username)
        selected_samples = request.session['selected_samples']
        orderno = generateorderno()
        if request.method == "POST":
            if(type(selected_samples)!=str):
                selected_samples = ",".join(selected_samples)
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            sampletype = request.POST.get("select-type")
            new_order = Order(orderno=orderno, username=username,  name=name, email=email,
                              phone=phone, selected_samples=selected_samples, sampletype=sampletype)
            new_order.save()
            del request.session['selected_samples']
            return render(request, 'dashboards/orderplaced.html')
        else:
            dname = username_object.name
            demail = username_object.email
            dphone = username_object.phone
            context = {
                'orderno': orderno,
                'selected_samples': selected_samples,
                'name': dname,
                'email': demail,
                'phone': dphone
            }
            return render(request, 'dashboards/sampling_order.html', context)
    else:
        return redirect('signin')
