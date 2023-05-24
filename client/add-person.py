
import envImport  # this has to be first
import authentication

from faker import Faker
fake = Faker()

person = authentication.createPerson(fake.random_number(
    digits=7), "401", "test")

print(person)
