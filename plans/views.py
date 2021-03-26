from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm
from django.urls import reverse_lazy
from django.views import generic
from .models import FitnessPlan, Customer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from django.http import HttpResponse

stripe.api_key = 'sk_test_51ITpKBDznegpUcupyUdBtFAujprxB18R5wd2puTcOkfQus4R06AiHhsg6GAHmxHH3BszES61BN9bcvfPjnh9cSDs003db5cL09'

def home(request):
    plans = FitnessPlan.objects
    return render(request, 'plans/home.html', {'plans':plans})

def plan(request,pk):
    plan = get_object_or_404(FitnessPlan, pk=pk)
    if plan.premium:
        # Checks - Is there an authneticated user?
        if request.user.is_authenticated:
            try:
                # Does user have a membership? It is now true
                # cause of the line below, instantiation of user
                if request.user.customer.membership:
                    return render(request, 'plans/plan.html', {'plan':plan})
            # This except checks specifically if customer doesn't exists
            except Customer.DoesNotExist:
                return redirect('join')    
        return redirect('join')
    else:
        return render(request, 'plans/plan.html', {'plan':plan})

def join(request):
    return render(request, 'plans/join.html')

@login_required
def checkout(request):
    # Prevents user from accessing a membership if they already
    # have one
    if request.user.is_authenticated:
        try:
            if request.user.customer.membership:
                return redirect('settings')
        except Customer.DoesNotExist:
            pass


    # continue to add values to this dict to create new coupons
    coupons = {'newyear': 35, 'birthday': 20, 'welcome': 23}

    # Create a customer and process payment
    if request.method == 'POST':
        # Create customer in Stripe
        stripe_customer = stripe.Customer.create(email= request.user.email,
                    source= request.POST['stripeToken'])
        # Specify plan: montly vs yearly. Comes from Stripe
        plan = 'price_1ITpdvDznegpUcupJyq5Hgwd'
        if request.POST['plan'] == 'yearly':
            plan = 'price_1ITpbIDznegpUcupavhymZrQ'
        
        # If user inputs a coupon, use such coupon - Add recurrence of coupon
        if request.POST['coupon'] in coupons:
            percentage = coupons[request.POST['coupon'].lower()]
            # Try to create a new coupon if it does not already exist in Stripe.  
            try:
                coupon = stripe.Coupon.create(duration= 'once', id= request.POST['coupon'].lower(),
                percent_off= percentage)
            except:
                pass
            subsciption = stripe.Subscription.create(customer= stripe_customer.id,
            items= [{'plan': plan}], coupon= request.POST['coupon'].lower())
        else:
            subsciption = stripe.Subscription.create(customer= stripe_customer.id,
            items= [{'plan': plan}])

        # Create a new customer - give them access to perks
        customer = Customer()
        customer.user = request.user
        customer.stripeid = stripe_customer.id
        # Customers will now have a membership. Those with
        # membership == True will be able to access content.
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = subsciption.id
        customer.save()

        return redirect('home')
    else:
        # Changes ammount depending on membership
        plan = 'monthly'
        coupon = 'none'
        price = 1000
        og_dollar = 10
        coupon_dollar = 0
        final_dollar = 10
         
        # If statements check url (monthy vs yearly) See join.html
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'yearly':
                plan = 'yearly'
                price = 10000
                og_dollar = 100
                final_dollar = 100
        
        # Checks if there is a coupon, which one it is and modifies
        if request.method == 'GET' and 'coupon' in request.GET:
            if request.GET['coupon'].lower() in coupons:
                 coupon = request.GET['coupon'].lower()
                 percentage = coupons[coupon]
                 coupon_price = int((percentage / 100) * price)
                 price = price - coupon_price
                 coupon_dollar = str(coupon_price)[:-2] + '.' + str(coupon_price)[-2:]
                 final_dollar = str(price)[:-2] + '.' + str(price)[-2:]

        return render(request, 'plans/checkout.html', {'coupon': coupon,
                'price': price, 'og_dollar': og_dollar, 'coupon_dollar': coupon_dollar,
                'final_dollar': final_dollar, 'plan': plan })

def settings(request):
    ''' Allows user to cancel their membership '''
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        # Retrieving subscription from user
        # subscription = stripe.Subscription.retrieve(request.user.Customer)
        # # Once subscription runs out, it will stop
        # subscription.cancel_at_period_end = True
        # request.user.customer.cancel_at_period_end = True
        # Update variable
        cancel_at_period_end = True
        # Sends info to Stripe API - so simple ;0)
        # subscription.save()
        # Update current user
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False 

    return render(request, 'registration/settings.html', {'membership': membership,
                        'cancel_at_period_end': cancel_at_period_end})

# @user_passes_test(lambda u: u.is_superuser)
# def updateaccounts(request):
#     customers = Customer.objects.all()
#     for customer in customers:
#         subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
#         if subscription.status != 'active':
#             customer.membership = False
#         else:
#             customer.membership = True
#         customer.cancel_at_period_end = subscription.cancel_at_period_end
#         customer.save()
#     return HttpResponse('completed')

# Class-based component
class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid
