

## Installation steps

1) clone the project  - ```https://github.com/JoseAntony07/Social-Network.git```
2) run the project    - 1. ```docker-compose build && docker-compose up``` or use normal method
                        2. ```activate venv``` and run the project
3) postman collection - ```https://api.postman.com/collections/20653730-165acf22-3657-4c0a-8cb5-130b851b3371?access_key=PMAT-01HH2KCGXJ938E4H02RWPZER2C```

## Api Endpoints

- Authentication - Jwt cookie auth
- BASE_URL - http://0.0.0.0:8000

```
1) Register User                  - POST   - BASE_URL/api/register/                                                                 
2) Login User                     - POST   - BASE_URL/api/login/                          
3) Logout User                    - POST   - BASE_URL/api/logout/                            
4) List All Users                 - GET    - BASE_URL/api/user/?search=antony&page=1            
5) List Accepted Friend Request   - GET    - BASE_URL/api/user/?page=1&query=accepted_friends    
6) List Received Friend Request   - GET    - BASE_URL/api/user/?page=1&query=pending_requests    

7) Send Friend Request            - PATCH  - BASE_URL/api/user/f4744489-d7e2-4b81-9fd7-20b10d9a9d3e/send_friend_request/   
                                             user_1 id - f4744489-d7e2-4b81-9fd7-20b10d9a9d3e
                                             user_2 id - request body - {
                                                                            "user_id": "ca20eb47-a00d-4c4d-827b-b12dff0b7278"
                                                                        }

8) Accept Friend Request          - PATCH  - BASE_URL/api/user/ca20eb47-a00d-4c4d-827b-b12dff0b7278/accept_friend_request/e5de9f0c-1cdc-424f-bab1-929c578adb63/
                                             user_2 id(received user) -  ca20eb47-a00d-4c4d-827b-b12dff0b7278
                                             friend request id - e5de9f0c-1cdc-424f-bab1-929c578adb63(id from List Received Friend Request Api)

9) Reject Friend Request          - PATCH  - BASE_URL/api/user/ca20eb47-a00d-4c4d-827b-b12dff0b7278/reject_friend_request/874679f7-acbb-4630-8882-1ebdd9b64b72/
                                             user_2 id(received user) -  ca20eb47-a00d-4c4d-827b-b12dff0b7278
                                             friend request id - 874679f7-acbb-4630-8882-1ebdd9b64b72(id from List Received Friend Request Api)                                       
```
