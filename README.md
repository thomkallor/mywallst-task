### The application in deployed using github actions in AWS ECS and the link to the swagger is down below:
http://ec2-3-132-215-210.us-east-2.compute.amazonaws.com/swagger/

user_id - The id of the user (I have already created a default admin user through migrations the user_id of this user is 1)

method_id - The payment method's stripe_id created by the user

price_id - The price_id(stripe's) to subscribe to. I already created products and price and a price_id that can be used (pm_1Hvq6xEtUponlBUM5rQ1Otrr)



### The application consists of 
## 1.An API for payment method creation:
POST /paymentmethod/{user_id}

## 2.An API for updating default payment method
PUT /customer/{user_id}/{method_id}

## 3.An API to create a subscription for the user
POST /subscription/{user_id}/{method_id}

## 4.An API to handle webhooks
POST /webhook

To Test the application use the POST /api/token to login

The credentials are:

username: admin

password: password

![alt text](https://i.ibb.co/fdsDbv0/example-login.png)

Copy the access token from the response

![alt text](https://i.ibb.co/k1hC6Jz/example-token.png)

Add '''Bearer ''' an empty space in front of the token and set the header using Authorize button:

![alt text](https://i.ibb.co/J75SBqC/token-setting.png)

## You can also view the admin page at:
(Same credentials as mentioned above)

http://ec2-3-132-215-210.us-east-2.compute.amazonaws.com/admin

### To run the applicaton locally do:
pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

You can run a docker container if that is more comfortable:
Just run 
## docker-compose up 
in the root directory

Both these methods should make the application available on:

http://localhost:8000

I am including a postman collection to make it easier if you want to play around with the APIs but still the Authorization header needs to be set:

The file is in the root directory mytask.postman_collection.json

