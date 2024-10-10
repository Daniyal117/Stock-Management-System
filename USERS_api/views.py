import json
from drf_yasg import openapi
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from .model import User, StockData, Transactions_table
from .serializer import User_serializer, StockData_serializer, Transactions_table_serializer

# List and Create view for User
class UserRegisterView(APIView): 

    @swagger_auto_schema(
        operation_description="Register a new user with a unique username and initial balance",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Username': openapi.Schema(type=openapi.TYPE_STRING, description="The unique username for the user"),
                'balance': openapi.Schema(type=openapi.TYPE_INTEGER, description="The initial balance of the user"),
            },
        ),
        responses={
            201: User_serializer,
            400: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            })
        },
    )
    def post(self, request):
        data = request.data
        username = data.get('Username')
        balance = data.get('balance')

        # Validate if the username is provided and balance is positive
        if not username or balance is None:
            return Response({"error": "Username and balance are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        if User.objects.filter(Username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User(Username=username, balance=balance)
        user.save()

        # Serialize the user data
        serializer = User_serializer(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# GET /users/{username}/: To retrieve user data
class UserDetailView(APIView):

    def get(self, request, username):
        # Check if the user data is available in the Redis cache
        cache_key = f"user_data_{username}"  # Unique cache key for user data
        cached_data = cache.get(cache_key)

        if cached_data:
            # If the data is found in the cache, return it
            return Response(cached_data, status=status.HTTP_200_OK)

        # If not found in cache, query the database
        user = get_object_or_404(User, Username=username)
        serializer = User_serializer(user)

        # Store the serialized data in Redis cache
        cache.set(cache_key, serializer.data, timeout=60*60)  # Cache for 1 hour

        # Return the user data
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    # DELETE /users/{username}/delete/: To delete a specific user
    def delete(self, request, username):
        user = get_object_or_404(User, Username=username)
        user.delete()

        cache_key = f"user_data_{username}"
        cache.delete(cache_key)

        return Response({"message": "User deleted successfully."},  status=status.HTTP_200_OK)

class UserALLDelete(APIView):
    def delete(self,request):
        User.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
              
class StockDataListCreate(APIView):
        # POST /stocks/: To ingest stock data
    @swagger_auto_schema(
        operation_description="Ingest stock data and store it in the Postgres database",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ticker': openapi.Schema(type=openapi.TYPE_STRING, description="The stock ticker symbol"),
                'open_price': openapi.Schema(type=openapi.TYPE_INTEGER, description="The opening price of the stock"),
                'close_price': openapi.Schema(type=openapi.TYPE_INTEGER, description="The closing price of the stock"),
                'high': openapi.Schema(type=openapi.TYPE_INTEGER, description="The highest price of the stock"),
                'low': openapi.Schema(type=openapi.TYPE_INTEGER, description="The lowest price of the stock"),
                'volume': openapi.Schema(type=openapi.TYPE_STRING, description="The trading volume of the stock"),
                'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="The timestamp of the stock data"),
            },
        ),
        responses={
            201: openapi.Response('Created', StockData_serializer),
            400: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }),
        },
    )
    def post(self, request):
        serializer = StockData_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Invalidate cache when new stock data is added
            cache.delete('all_stock_data')  # Clear cache for all stocks
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET /stocks/: To retrieve all stock data (with Redis caching)
    def get(self, request):
        # Check if data is cached in Redis
        cached_stock_data = cache.get('all_stock_data')
        if cached_stock_data:
            return Response(json.loads(cached_stock_data), status=status.HTTP_200_OK)

        # If not cached, fetch from the database
        stock_data = StockData.objects.all()
        serializer = StockData_serializer(stock_data, many=True)

        # Cache the result in Redis (set a timeout if necessary)
        cache.set('all_stock_data', json.dumps(serializer.data), timeout=60*10)  # Cache for 10 minutes

        return Response(serializer.data, status=status.HTTP_200_OK)

class StockDataDetail(APIView):
    # GET /stocks/{ticker}/: To retrieve specific stock data (with Redis caching)
    def get(self, request, ticker):
        cache_key = f'stock_data_{ticker}'
        
        # Check if specific stock data is cached in Redis
        cached_stock = cache.get(cache_key)
        if cached_stock:
            return Response(json.loads(cached_stock), status=status.HTTP_200_OK)

        # If not cached, fetch from the database
        
        # stock_data = get_object_or_404(StockData, ticker=ticker)
        stock_data = StockData.objects.get(ticker=ticker)

        serializer = StockData_serializer(stock_data)

        # Cache the specific stock data in Redis (set a timeout if necessary)
        cache.set(cache_key, json.dumps(serializer.data), timeout=60*10)  # Cache for 10 minutes

        return Response(serializer.data, status=status.HTTP_200_OK)

class TransactionCreate(APIView):
    # Swagger documentation for POST /transactions/
    @swagger_auto_schema(
        operation_description="Create a new transaction (buy stock)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['Username', 'ticker', 'transaction_type', 'transaction_volume'],
            properties={
                'Username': openapi.Schema(type=openapi.TYPE_STRING, description="The Name of the user"),
                'ticker': openapi.Schema(type=openapi.TYPE_STRING, description="The stock ticker symbol"),
                'transaction_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['buy'],
                    description="The type of transaction (buy)"
                ),
                'transaction_volume': openapi.Schema(type=openapi.TYPE_INTEGER, description="The volume of stock for the transaction")
            },
        ),
        responses={
            201: openapi.Response('Transaction successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
        }
    )
    def post(self, request):
        Username = request.data.get('Username')
        ticker = request.data.get('ticker')
        transaction_type = request.data.get('transaction_type')
        transaction_volume =request.data.get('transaction_volume')

        # Get user and stock data
        user = get_object_or_404(User,Username=Username)
        stock = get_object_or_404(StockData, ticker=ticker)
        print(type(stock))
        # Calculate transaction price based on the current stock price
        transaction_price = stock.close_price * transaction_volume

        # Handle balance for buy/sell
        if transaction_type == 'buy':
            if user.balance > transaction_price and user.balance>0:
                user.balance -= transaction_price
                if user.balance<0:
                    user.balance=0
            else:  
                return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)            
        # Update user's balance 
        user.save()
        cache_key = f"user_data_{user.Username}"
        cache.delete(cache_key)
        # Updating stock volume
        stock.volume =str(int(stock.volume)-transaction_volume)
        stock.save()
        cache_key = f"all_stock_data{stock.volume}"
        cache.delete(cache_key)
        # save the transaction
        transaction = Transactions_table(
            user=user,
            ticker=stock,
            transaction_type=transaction_type,
            transaction_volume=int(transaction_volume),
            transaction_price=transaction_price,
            timestamp=timezone.now()
        )
        transaction.save()
        return Response({"message": "Transaction successful"}, status=status.HTTP_201_CREATED)
    
class UserTransactions(APIView):
    # GET /transactions/{username}/: To retrieve all transactions of a specific user
    def get(self, request, username):
        try:
            # Find the user by username 
            user = User.objects.get(Username=username)  # Assuming Username is the correct field name
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        transactions = Transactions_table.objects.filter(user=user) 
        
        if not transactions.exists():  
            return Response({"error": "No transactions found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = Transactions_table_serializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
