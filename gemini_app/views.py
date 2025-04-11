# from django.shortcuts import render
# from django.http import HttpResponse
# import google.generativeai as genai
# from django.shortcuts import render

# genai.configure(api_key="AIzaSyA62GAHTjnfqI602xCxTzNEnW4k6uQ-LOw")

# model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# def chat_page(request):
#     user_message = ""
#     gemini_response = ""
#     if request.method == 'POST':
#         user_message = request.POST.get('prompt')
#         try:
#             response = model.generate_content(user_message)
#             gemini_response = response.text
#         except Exception as e:
#             gemini_response = "Something went wrong \n" + str(e)

#     return render(request, 'chat.html', {
#         'user_message': user_message,
#         'gemini_response': gemini_response
#     })
# def login_view(request):
#     # your login logic here
#     return render(request, 'login.html')

# def signup_view(request):
#     # your signup logic here
#     return render(request, 'signup.html')

from django.shortcuts import render,redirect
import google.generativeai as genai

genai.configure(api_key="AIzaSyA62GAHTjnfqI602xCxTzNEnW4k6uQ-LOw")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

def chat_page(request):
    # Get previous conversation from session, or initialize
    conversation = request.session.get('conversation', [])

    if request.method == 'POST':
        user_message = request.POST.get('query')  # changed to 'query' as in HTML
        try:
            response = model.generate_content(user_message)
            gemini_response = response.text
        except Exception as e:
            gemini_response = "Something went wrong \n" + str(e)

        # Append to conversation
        conversation.append({
            'query': user_message,
            'response': gemini_response
        })
        request.session['conversation'] = conversation  # save to session

    return render(request, 'chat.html', {
        'conversation': conversation
    })

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def clear_chat(request):
    request.session['conversation'] = []
    return redirect('chat')

