import graphene

# Définition du schéma GraphQL
class User(graphene.ObjectType):
   id = graphene.Int()
   name = graphene.String()

class Query(graphene.ObjectType):
   users = graphene.List(User)

   def resolve_users(self, info):
       return [{'id': 1, 'name': "Alice"},   
               {'id': 2, 'name': "Bob"}]
   

   


schema = graphene.Schema(query=Query)