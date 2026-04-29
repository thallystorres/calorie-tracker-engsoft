@startuml
skinparam componentStyle rectangle
skinparam packageStyle rectangle
hide empty members

package "Camada de Controladores" {

class AccountsController << (C,lightblue) >> { + register(request): Response + login(request): Response + activate(request): Response + get_me(request): Response + request_password_reset(request): Response
}

class ProfilesController << (C,lightblue) >> { + create_profile(request): Response + update_profile(request): Response + add_food_restriction(request): Response + delete_food_restriction(request, pk): Response
}

class FoodsController << (C,lightblue) >> { + list_foods(request): Response + create_food(request): Response + get_food(request, food_id): Response + log_food_meal(request): Response
}

class TrackerController << (C,lightblue) >> { + create_meal(request): Response
}
}

package "Camada de Serviços (Application)" {

class UserService << (S,lightgreen) >> { + create_account(data): User + update_account(user, data): User + authenticate_account(login, password): User + activate_account(token): User + request_password_reset(email)
}

class ProfileService << (S,lightgreen) >> { + upsert_profile(profile, data): NutritionalProfile + calculate_bmr(weight, height, age, sex): Decimal + calculate_daily_target(bmr, activity_level, goal): Decimal
}

class FoodService << (S,lightgreen) >> { + list_foods(query): Food[] + get_food_or_404(food_id): Food + create_food(data): Food
}

class TrackerService << (S,lightgreen) >> { + log_food(user, data): MealLog + create_meal(user, data): Meal
}
}

package "Camada de Domínio (Entities)" {

class User << (E,orange) >>
class NutritionalProfile << (E,orange) >>
class Food << (E,orange) >>
class Meal << (E,orange) >>
class MealLog << (E,orange) >>
}

package "Camada de Regras de Negócio" {

abstract class BaseSignedTokenService << (B,lightyellow) >> { + generate(user): str + validate(token): (int, str)
}

class ActivationTokenService << (B,lightyellow) >>
class PasswordResetTokenService << (B,lightyellow) >>

abstract class BaseEmailService << (B,lightyellow) >> { + send_email(user, token, request) + build_message(user, url): str
}

class ActivationEmailService << (B,lightyellow) >>
class PasswordResetEmailService << (B,lightyellow) >>
}

' Controller → Service

AccountsController --> UserService
ProfilesController --> ProfileService
FoodsController --> FoodService
FoodsController --> TrackerService
TrackerController --> TrackerService

' Service → Entities

UserService --> User
ProfileService --> NutritionalProfile
FoodService --> Food
TrackerService --> Meal
TrackerService --> MealLog

' Service → Business Logic

UserService --> ActivationTokenService
UserService --> PasswordResetTokenService
UserService --> ActivationEmailService
UserService --> PasswordResetEmailService

' Herança

ActivationTokenService --|> BaseSignedTokenService
PasswordResetTokenService --|> BaseSignedTokenService

ActivationEmailService --|> BaseEmailService
PasswordResetEmailService --|> BaseEmailService

note right of AccountsController
<u>Legenda</u>

Pacote: camada arquitetural
Seta sólida: dependência
Seta com triângulo: herança

Cores:
Azul = Controladores
Verde = Serviços
Laranja = Entidades
Amarelo = Regras de negócio

Excluído:
UI / Frontend
Persistência (ORM / DB)
end note

@enduml
