class Pet:
    def __init__(self, name, pet_type, color):
        self.name = name
        self.type = pet_type
        self.hunger = 0
        self.happiness = 100
        self.age = 0
        self.color = color

    def feed(self):
        self.hunger = max(0, self.hunger - 10)
        self.happiness += 5

    def age_pet(self):
        self.age += 1
        self.hunger += 5
        self.happiness -= 5

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'hunger': self.hunger,
            'happiness': self.happiness,
            'age': self.age,
            'color': self.color
        }


class Mii:
    def __init__(self, name):
        self.name = name
        self.pet = None  # New pet attribute


class GameState:
    def __init__(self):
        self.pets = []  # List to manage pets

    def add_pet(self, pet):
        self.pets.append(pet)

    def feed_pet(self, pet_name):
        for pet in self.pets:
            if pet.name == pet_name:
                pet.feed()
                return
        print(f"Pet named {pet_name} not found.")

    def age_all_pets(self):
        for pet in self.pets:
            pet.age_pet()

    def get_pets_info(self):
        return [pet.to_dict() for pet in self.pets]
