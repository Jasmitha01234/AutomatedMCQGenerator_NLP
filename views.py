from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseServerError
from django.views import debug
from django.conf import settings
from userapp.models import *
import urllib.request
import time
import urllib.parse
import random
import re

# Create your views here.
def sendSMS(user, otp, mobile):
    data = urllib.parse.urlencode({
        'username': 'Codebook',
        'apikey': '56dbbdc9cea86b276f6c',
        'mobile': mobile,
        'message': f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you',
        'senderid': 'CODEBK'
    })
    data = data.encode('utf-8')
    # Disable SSL certificate verification
    # context = ssl._create_unverified_context()
    request = urllib.request.Request("https://smslogin.co/v3/api.php?")
    f = urllib.request.urlopen(request, data)
    return f.read()
# Create your views here.
def user_index(request):
    messages.success(request,'login successfull')

    return render(request, 'index.html')


def user_result(request):
    mcqs = request.session.get('mcqs')
    return render(request, 'result.html',{'mcqs':mcqs})

def user_courses(request):
    return render(request, 'courses.html')

def user_contact(request):
    return render(request, 'contact.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        email = request.POST.get('email_address')
        password = request.POST.get('email_password')
        number = request.POST.get('contact_number')
        file = request.FILES['user_file']
        print(request)
        print(username, email, password, number, file, 'data')
        otp = str(random.randint(1000, 9999))
        print(otp, 'generated otp')
        try:
            UserMCQsModels.objects.get(user_email = email)
            messages.info(request, 'mail already registered')
            return redirect('register')
        except:
            mail_message = f'Registration Successfully\n Your 4 digit Pin is below\n {otp}'
            print(mail_message)
            send_mail("Student Password", mail_message , settings.EMAIL_HOST_USER, [email])
            # text message
            sendSMS(username, otp, number)
        
            UserMCQsModels.objects.create(otp=otp, user_contact = number, user_username = username, user_email = email, user_password = password, user_file = file)
            request.session['user_email'] = email
            return redirect('otp')
    return render(request, 'user-register.html')

def user_otp(request):
    user_id = request.session['user_email']
    user =UserMCQsModels.objects.get(user_email = user_id)
    messages.success(request, 'OTP  Sent successfully')
    print(user_id)
    print(user, 'user avilable')
    print(type(user.otp))
    print(user. otp, 'creaetd otp')   
    if request.method == 'POST':
        u_otp = request.POST.get('otp')
        u_otp = int(u_otp)
        print(u_otp, 'enter otp')
        if u_otp == user.otp:
            print('if')
            user.otp_status  = 'verified'
            user.save()
            messages.success(request, 'OTP  verified successfully')
            return redirect('user')
        else:
            print('else')
            messages.error(request, 'Invalid OTP') 
            return redirect('otp')
    return render(request, 'user-otp.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email_address')
        password = request.POST.get('email_password')
        print(email, password)
        try:
            user = UserMCQsModels.objects.get(user_email = email, user_password = password)
            print(user)
            request.session['user_id'] = user.user_id
            a = request.session['user_id']
            print(a)

            if user.user_password ==  password :
                    if user.otp_status == 'verified':
                        messages.success(request,'login successfull')
                        request.session['user_id'] = user.user_id
                        print('login sucessfull')
                        user.No_Of_Times_Login += 1
                        user.save()
                        return redirect('dashboard')
                    else:
                         return redirect('otp')
            else:
                 messages.error(request,'Login credentials was incorrect...')
        except:
            messages.error(request,'Login credentials was incorrect...')
            print(';invalid credentials')
            print('exce')

            return redirect('user')
    return render(request, 'user-login.html')




def user_dashboard(request):
    return render(request, 'user-dashboard.html')

def user_myprofile(request):
    views_id = request.session['user_id']
    user = UserMCQsModels.objects.get(user_id = views_id)
    print(user, 'user_id')
    if request.method =='POST':
        username = request.POST.get('user_name')
        email = request.POST.get('email_address')
        number = request.POST.get('contact_number')
        password = request.POST.get('email_password')
        date = request.POST.get('date')
        print(username, email, number, password, date, 'data') 

        user.user_username = username
        user.user_email = email
        user.user_contact = number
        user.user_password = password
        user.user_dates = date 

        if len(request.FILES)!=0:
            file = request.FILES['user_file']
            user.user_file = file
            user.user_username = username
            user.user_email = email
            user.user_contact = number
            user.user_password = password
            user.save()
        else:
            user.user_username = username
            user.user_email = email
            user.user_contact = number
            user.user_password = password
            user.save()

    return render(request, 'user-profile.html', {'i':user})


import nltk
import random
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.chunk import tree2conlltags

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('wordnet')






def extract_keywords(text):
    sentences = sent_tokenize(text)
    words = [word_tokenize(sent) for sent in sentences]
    pos_tags = [pos_tag(word) for word in words]
    named_entities = [ne_chunk(tag) for tag in pos_tags]
    named_entities_tags = [tree2conlltags(ne) for ne in named_entities]

    keywords = []
    for sent in named_entities_tags:
        for word, tag, chunk in sent:
            if chunk != 'O':
                keywords.append(word)
    
    return list(set(keywords))

def create_mcq(text):
    keywords = extract_keywords(text)
    questions = []
    for keyword in keywords:
        sentences = sent_tokenize(text)
        sentence = next((sent for sent in sentences if keyword in sent), None)
        if sentence:
            question = sentence.replace(keyword, "")
            distractors = generate_distractors(keyword)
            if len(distractors) < 3:
                continue
            options = distractors + [keyword]
            random.shuffle(options)
            questions.append({
                'question': question,
                'options': options,
                'answer': keyword
            })
    return questions

def generate_distractors(answer, num_distractors=3):
    distractors = set()
    synsets = wn.synsets(answer)
    if not synsets:
        return list(distractors)
    for syn in synsets:
        for lemma in syn.lemmas():
            if lemma.name().lower() != answer.lower():
                distractors.add(lemma.name().replace('_', ' '))
            if len(distractors) >= num_distractors:
                break
        if len(distractors) >= num_distractors:
            break
    return list(distractors)



def user_detection(request):
    if request.method == 'POST':
        # Display MCQs
        text = request.POST.get('mood_pred', '')
        mcqs = create_mcq(text)
        for i, mcq in enumerate(mcqs):
            print(f"Q{i+1}: {mcq['question']}")
            for j, option in enumerate(mcq['options']):
                print(f"  {chr(65+j)}. {option}")
            print(f"Answer: {mcq['answer']}")
            request.session['mcqs'] = mcqs
            return redirect ('result')
    return render(request, 'mcq-detection.html')


