import json
import base64
import hashlib
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError

def initiate_payment(request):
    if request.method == 'POST':
        amount = int(request.POST.get('amountEnterByUsers'))*100

        payload_data = {
            "merchantId": "PGTESTPAYUAT101",
            "merchantTransactionId": "MT7850590068188104",
            "merchantUserId": "MUID123",
            "amount": amount,
            "redirectUrl": "https://google.com",
            "redirectMode": "POST",
            "callbackUrl": "https://in.yahoo.com",
            "mobileNumber": "9999999999",
            "paymentInstrument": {
                "type": "PAY_PAGE",
            },
        }

        encoded_payload = base64.b64encode(json.dumps(payload_data).encode()).decode()
        salt_key = "4c1eba6b-c8a8-44d3-9f8b-fe6402f037f3"
        salt_index = 1
        string = f"{encoded_payload}/pg/v1/pay{salt_key}"
        sha256 = hashlib.sha256(string.encode()).hexdigest()
        final_x_header = f"{sha256}###{salt_index}"
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": final_x_header,
        }

        phone_pay_url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
        response = requests.post(
            phone_pay_url,
            json={"request": encoded_payload},
            headers=headers
        )
        print(response)
        try:
            if response.status_code == 200:
                response_data = response.json()
                url = response_data['data']['instrumentResponse']['redirectInfo']['url']
                return redirect(url)
            else:
                error_message = "Payment initiation failed"
                return render(request, 'failed.html', {'error_message': error_message})
        except json.JSONDecodeError as e:
            error_message = f"Error decoding JSON response: {str(e)}"
            return render(request, 'failed.html', {'error_message': error_message})
        except Exception as e:
            return HttpResponseServerError(f"An error occurred: {str(e)}")

    return render(request, 'payment_form.html')